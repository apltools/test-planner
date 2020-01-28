import datetime as dt
from collections import defaultdict
from typing import DefaultDict, ItemsView, List
from uuid import uuid4

import django.utils.timezone as tz
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template.defaultfilters import time as _time
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _

TimeAppointmentsTuple = ItemsView[dt.time, List['Appointment']]


def add_time(time: dt.time, *, hours: int = 0, minutes: int = 0) -> dt.time:
    return (dt.datetime.combine(dt.date.today(), time) + dt.timedelta(hours=hours, minutes=minutes)).time()


def subtract_time(time: dt.time, *, hours: int = 0, minutes: int = 0) -> dt.time:
    return (dt.datetime.combine(dt.date.today(), time) - dt.timedelta(hours=hours, minutes=minutes)).time()


def get_cancel_secret(length: int = 64) -> str:
    return get_random_string(length=length)


class User(AbstractUser):
    pass


"""NEW"""


class EventInfo(models.Model):
    _host = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    _slot_length = models.IntegerField(blank=True, null=True)
    _location = models.fields.CharField(max_length=16, blank=True, null=True)
    _extras = JSONField(blank=True, null=True)

    class Meta:
        abstract = True


class EventType(EventInfo):
    name = models.CharField(max_length=64, unique=True, null=True)
    slug = models.SlugField(max_length=16, unique=True, null=True)

    def __str__(self):
        return self.name

    class Meta(EventInfo.Meta):
        pass


class Event(EventInfo):
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='events')

    date = models.DateField(verbose_name=_("Datum"))
    start_time = models.TimeField(verbose_name=_("Start Tijd"))
    end_time = models.TimeField(verbose_name=_("Eind Tijd"))

    def time_string(self):
        return f'{_time(self.start_time)} tot {_time(self.end_time)}'

    time_string.short_description = "Tijden"

    def slot_length(self) -> int:
        return self._slot_length if self._slot_length else self.event_type._slot_length

    def location(self) -> str:
        return self._location if self._location else self.event_type._location

    location.short_description = _("Locatie")

    @property
    def host(self) -> User:
        return self._host if self._host else self.event_type._host

    @property
    def slots(self) -> List[dt.time]:
        """List of possible time slots."""
        if not self.slot_length:
            return []
        cur_time = self.start_time

        slots_list: List[dt.time] = [cur_time]

        while (cur_time := add_time(cur_time, minutes=self.slot_length)) < self.end_time:
            slots_list.append(cur_time)

        return slots_list

    @property
    def extras(self):
        event_extras = self.event_type._extras
        own_extras = self._extras
        if event_extras and own_extras:
            event_extras.update(own_extras)
            return event_extras
        elif own_extras:
            return own_extras
        elif event_extras:
            return event_extras
        return None

    class Meta(EventInfo.Meta):
        pass


class EventAppointment(models.Model):
    # Student info
    name = models.CharField(max_length=32)
    student_nr = models.PositiveIntegerField()

    # Date/Time
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    created = models.DateTimeField(auto_now_add=True)


"""ENDOFNEW"""


class Course(models.Model):
    name = models.fields.CharField(max_length=64, verbose_name='Naam')
    short_name = models.fields.SlugField(max_length=16)

    def __str__(self):
        return self.short_name

    def tests_this_week(self) -> List['TestMoment']:
        """Returns TestMoments in the coming week, including today if there are slots in the future."""
        today = tz.localdate()
        next_week = today + dt.timedelta(weeks=1)

        test_moments = self.test_moments.filter(date__gte=today, date__lte=next_week, hidden_from_total=False).order_by(
            'date')

        return [moment for moment in test_moments if
                moment.date > today or moment.last_slot.time > tz.localtime().time()]

    class Meta:
        verbose_name = _("Vak")
        verbose_name_plural = _("Vakken")


class TimeOption:
    def __init__(self, time: dt.time, available: bool = True):
        self.time: dt.time = time
        self.available: bool = available

    class Meta:
        managed = False


class AbstractMoment(models.Model):
    location = models.fields.CharField(max_length=16, verbose_name=_("Locatie"))
    date = models.fields.DateField(verbose_name=_("Datum"))
    start_time = models.fields.TimeField(verbose_name=_("Begintijd"))
    end_time = models.fields.TimeField(verbose_name=_("Eindtijd"))
    hidden_from_total = models.fields.BooleanField(default=False, verbose_name=_("Verborgen"))

    def time_string(self):
        return f'{_time(self.start_time)} tot {_time(self.end_time)}'

    time_string.short_description = "Tijden"

    def __str__(self) -> str:
        return f'{self.date} van {self.start_time} tot {self.end_time}'

    class Meta:
        abstract = True

        ordering = ('-date', 'start_time')


class TestMoment(AbstractMoment):
    """Model for range in time in which tests can be planned."""

    test_length = models.fields.IntegerField(verbose_name=_("Toetslengte"), default=15)
    max_tests = models.fields.IntegerField(verbose_name=_('Aantal toetsjes'), default=3)

    courses = models.ManyToManyField(Course, through='CourseMomentRelation', related_name='test_moments',
                                     verbose_name=_("Vakken"))
    uuid = models.fields.UUIDField(default=uuid4)

    def course_name_list(self):
        return [course.name for course in self.courses.all()]

    course_name_list.short_description = "Vakken"

    @property
    def appointments_for_moment(self):
        apps_time: DefaultDict[str, List['Appointment']] = defaultdict(list)
        appointments = Appointment.objects.filter(date=self.date,
                                                  start_time__range=(self.start_time, self.end_time)).order_by(
            'start_time')
        for appointment in appointments:
            apps_time[str(appointment.start_time)[:-3]].append(appointment)
        return apps_time

    @property
    def slot_delta(self) -> dt.timedelta:
        """Slot length as a timedelta"""
        return dt.timedelta(minutes=self.test_length)

    @property
    def last_slot(self) -> TimeOption:
        return self.student_slots[-1]

    @property
    def student_slots(self) -> List[TimeOption]:
        """List of possible time slots."""
        cur_time = self.start_time

        slots: List[TimeOption] = []

        while add_time(cur_time, minutes=self.test_length) <= self.end_time:
            slots.append(TimeOption(cur_time))
            cur_time = add_time(cur_time, minutes=self.test_length)

        return slots

    def student_slots_for_course(self, course: Course) -> List[TimeOption]:
        slots = self.student_slots

        for slot in slots:
            slot.available = self.spots_available(slot.time, course)

        now = tz.localtime().time()

        # If slot is today, check if this slot hasn't started yet
        if self.date == tz.localdate():
            for slot in slots:
                if slot.time <= now:
                    slot.available = False

        return slots

    def spots_available(self, time: dt.time, course: Course) -> bool:
        appointments = Appointment.objects.filter(date__exact=self.date).filter(start_time__exact=time).filter(
            course=course).count()
        return appointments < self.coursemomentrelation_set.get(course=course).places

    class Meta(AbstractMoment.Meta):
        verbose_name = _("Toetsmoment")
        verbose_name_plural = _("Toetsmomenten")
        unique_together = ['start_time', 'end_time', 'location', 'date']


class CourseMomentRelation(models.Model):
    """Intermediate table for relation between Course and a TestMoment"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("Vak"))
    time_slot = models.ForeignKey(TestMoment, on_delete=models.CASCADE, verbose_name=_("Toetsmoment"))

    allowed_tests = models.ManyToManyField('Test', verbose_name=_("Toetsjes"))
    places = models.fields.IntegerField(verbose_name=_("Plekken"))
    description = models.fields.TextField(verbose_name=_("Beschrijving"), blank=True, default="")

    class Meta:
        unique_together = ('course', 'time_slot')


class Test(models.Model):
    name = models.fields.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _("Toetsje")
        verbose_name_plural = _("Toetsjes")


class Appointment(models.Model):
    student_name = models.fields.CharField(max_length=32, verbose_name=_("Naam"))
    email = models.fields.EmailField(verbose_name=_("E-mail"))
    student_nr = models.fields.IntegerField(verbose_name=_("Studentnummer"), null=True)
    date = models.fields.DateField(verbose_name=_("Datum"))
    start_time = models.fields.TimeField(verbose_name=_("Begintijd"))
    duration = models.fields.IntegerField(verbose_name=_("Lengte"))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("Vak"))
    cancel_secret = models.CharField(max_length=64, default=get_cancel_secret)

    tests = models.ManyToManyField(Test, verbose_name=_("Toetsjes"))

    @property
    def end_time(self) -> dt.time:
        return add_time(self.start_time, minutes=self.duration)

    def __str__(self) -> str:
        return f'{self.student_name} om {self.start_time} op {self.date}'

    class Meta:
        unique_together = ('student_nr', 'date')
        verbose_name = _("Afspraak")
        verbose_name_plural = _("Afspraken")
