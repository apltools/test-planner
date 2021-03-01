import datetime as dt
from typing import ItemsView, List

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import time as _time
from django.utils import timezone as tz
from django.utils.translation import gettext as _

from zoom.models import ZoomMeeting, OAuth2Token
from .helpers import add_time, gen_cancel_secret, validate_timeslot

TimeAppointmentsTuple = ItemsView[dt.time, List['Appointment']]


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


class EventType(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True)
    slug = models.SlugField(max_length=16, unique=True, null=True)


    slot_length = models.PositiveIntegerField(default=20, validators=[validate_timeslot])


    def __str__(self):
        return self.name

    def events_next_week(self):
        today = tz.localdate()
        next_week = today + dt.timedelta(weeks=1)
        return self.events.filter(date__gte=today, date__lte=next_week).order_by('date')


class Event(models.Model):
    """Represents a event, a moments on a day with one or multiple timeslots."""
    hosts = models.ManyToManyField(User)

    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='events')

    date = models.DateField(verbose_name=_("Datum"))
    start_time = models.TimeField(verbose_name=_("Starttijd"))

    @property
    def slots(self) -> List[TimeSlot]:
        """List of possible time slots."""
        cur_time = self.start_time

        slots_list: List[TimeSlot] = []

        while cur_time < add_time(self.start_time, hours=1):
            slots_list.append(TimeSlot(cur_time))

            cur_time = add_time(cur_time, minutes=self.event_type.slot_length)

        return slots_list

    # def slot_open(self, *, time: dt.time) -> bool:
    #     # Check is slot is in the past
    #     if tz.make_aware(dt.datetime.combine(self.date, time)) < tz.localtime():
    #         return False
    #
    #     apps_count = self.appointments_at_time(time=time).count()
    #     return apps_count < self.capacity_total()

    # def appointments_at_time(self, *, time: dt.time) -> QuerySet:
    #     apps = self.appointments.filter(start_time__exact=time)
    #     return apps

    def __str__(self):
        return self.event_type.slug

    class Meta:
        ordering = ['-date', '-start_time']


class EventAppointment(models.Model):
    # Student info
    name = models.CharField(max_length=32, verbose_name=_('Naam'))
    student_nr = models.PositiveIntegerField(verbose_name=_('Studentnummer'))
    email = models.EmailField()

    # Date/Time
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.PositiveSmallIntegerField()

    @property
    def end_time(self):
        return add_time(self.start_time, minutes=self.duration)

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
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='appointments'
    )

    # General info
    created = models.DateTimeField(auto_now_add=True)
    cancel_secret = models.CharField(max_length=64, default=gen_cancel_secret, unique=True)

    def time_string(self):
        return f'{_time(self.start_time)} tot {_time(self.end_time)}'

    time_string.short_description = "Tijden"

    class Meta:
        unique_together = ('student_nr', 'date')
        ordering = ['date', 'start_time']
