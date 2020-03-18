import datetime as dt
from typing import Dict, ItemsView, List, Optional
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import QuerySet
from django.template.defaultfilters import time as _time
from django.utils import timezone as tz
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from first import first

from zoom.models import ZoomMeeting, OAuth2Token

TimeAppointmentsTuple = ItemsView[dt.time, List['Appointment']]


def add_time(time: dt.time, *, hours: int = 0, minutes: int = 0) -> dt.time:
    return (dt.datetime.combine(dt.date.today(), time) + dt.timedelta(hours=hours, minutes=minutes)).time()


def subtract_time(time: dt.time, *, hours: int = 0, minutes: int = 0) -> dt.time:
    return (dt.datetime.combine(dt.date.today(), time) - dt.timedelta(hours=hours, minutes=minutes)).time()


def gen_cancel_secret(length: int = 64) -> str:
    return get_random_string(length=length)


class User(AbstractUser):
    is_teaching_assistant = models.BooleanField(default=False, verbose_name=_("Assistent"))

    def has_zoom_token(self) -> bool:
        return OAuth2Token.objects.filter(name='zoom', user=self).exists()


class TimeSlot:
    def __init__(self, time: dt.time, available: bool = True):
        self.time: dt.time = time
        self.available: bool = available

    class Meta:
        managed = False


class EventInfo(models.Model):
    _hosts = models.ManyToManyField(User)
    _slot_length = models.IntegerField(blank=True, null=True)
    _location = models.fields.CharField(max_length=16, blank=True, null=True)
    _extras = JSONField(blank=True, null=True)
    _capacity = models.PositiveIntegerField(verbose_name=_("Capaciteit per Host"), blank=True, null=True)
    _is_zoom_meeting = models.BooleanField(default=False, verbose_name="Zoom Meeting")

    class Meta:
        abstract = True


class EventType(EventInfo):
    name = models.CharField(max_length=64, unique=True, null=True)
    slug = models.SlugField(max_length=16, unique=True, null=True)

    def __str__(self):
        return self.name

    def events_next_week(self):
        today = tz.localdate()
        next_week = today + dt.timedelta(weeks=1)
        return self.events.filter(date__gte=today, date__lte=next_week).order_by('date')

    class Meta(EventInfo.Meta):
        pass


class Event(EventInfo):
    """Represents a event, a moments on a day with one or multiple timeslots."""
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='events')

    date = models.DateField(verbose_name=_("Datum"))
    start_time = models.TimeField(verbose_name=_("Start Tijd"))
    end_time = models.TimeField(verbose_name=_("Eind Tijd"))
    uuid = models.UUIDField(default=uuid4)

    def time_string(self):
        return f'{_time(self.start_time)} tot {_time(self.end_time)}'

    time_string.short_description = _("Tijden")

    def slot_length(self) -> int:
        return first([self._slot_length, self.event_type._slot_length])

    def location(self) -> str:
        return first([self._location, self.event_type._location])

    location.short_description = _("Locatie")

    def capacity(self) -> int:
        return first([self._capacity, self.event_type._capacity], default=1)

    def is_zoom_meeting(self) -> bool:
        return self._is_zoom_meeting or self.event_type._is_zoom_meeting

    is_zoom_meeting.short_description = _('Zoom Meeting')

    @property
    def hosts(self) -> Optional[User]:
        return first([self._hosts, self.event_type._hosts])

    @property
    def slots(self) -> List[TimeSlot]:
        """List of possible time slots."""
        if not self.slot_length or not self.start_time:
            return []

        cur_time = self.start_time

        slots_list: List[TimeSlot] = []
        while cur_time < self.end_time:
            slots_list.append(TimeSlot(cur_time, available=self.slot_open(time=cur_time)))

            cur_time = add_time(cur_time, minutes=self.slot_length())

        return slots_list

    @property
    def extras(self) -> Optional[Dict]:
        event_extras: Dict = self.event_type._extras
        own_extras: Dict = self._extras

        if event_extras and own_extras:
            event_extras.update(own_extras)
            return event_extras
        elif own_extras:
            return own_extras
        elif event_extras:
            return event_extras
        return None

    def extra_inputs(self) -> Optional[Dict]:
        if input := self.extras.get('input'):
            return input
        return None

    def slot_open(self, *, time: dt.time) -> bool:
        # Check is slot is in the past
        if tz.make_aware(dt.datetime.combine(self.date, time)) < tz.localtime():
            return False

        apps_count = self.appointments_at_time(time=time).count()
        return apps_count < self.capacity()

    def appointments_at_time(self, *, time: dt.time) -> QuerySet:
        apps = self.appointments.filter(start_time__exact=time)
        return apps

    def __str__(self):
        return self.event_type.slug

    class Meta(EventInfo.Meta):
        ordering = ['-date', '-start_time']


class EventAppointment(models.Model):
    # Student info
    name = models.CharField(max_length=32, verbose_name=_('Naam'))
    student_nr = models.PositiveIntegerField(verbose_name=_('Studentnummer'))
    email = models.EmailField()

    # Date/Time
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Appointment info
    host = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="event_appointments",
        null=True,
        blank=True
    )
    zoom_meeting = models.OneToOneField(
        ZoomMeeting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='appointments'
    )
    extras = JSONField(null=True, blank=True)

    # General info
    created = models.DateTimeField(auto_now_add=True)
    cancel_secret = models.CharField(max_length=64, default=gen_cancel_secret, unique=True)

    def time_string(self):
        return f'{_time(self.start_time)} tot {_time(self.end_time)}'

    time_string.short_description = "Tijden"

    class Meta:
        unique_together = ('student_nr', 'date')
        ordering = ['date', 'start_time']
