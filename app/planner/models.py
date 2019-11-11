import datetime as dt
from collections import defaultdict
from typing import DefaultDict, ItemsView, List
from uuid import uuid4

import django.utils.timezone as tz
from django.contrib.auth.models import AbstractUser
from django.db import models
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


class Course(models.Model):
    name = models.fields.CharField(max_length=64)
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


class TestMoment(models.Model):
    location = models.fields.CharField(max_length=16, verbose_name=_("Locatie"))
    date = models.fields.DateField(verbose_name=_("Datum"))
    start_time = models.fields.TimeField(verbose_name=_("Begintijd"))
    end_time = models.fields.TimeField(verbose_name=_("Eindtijd"))
    test_length = models.fields.IntegerField(verbose_name=_("Toetslengte"), default=15)
    hidden_from_total = models.fields.BooleanField(default=False, verbose_name=_("Verborgen"))

    courses = models.ManyToManyField(Course, through='CourseMoment', related_name='test_moments',
                                     verbose_name=_("Vakken"))
    uuid = models.fields.UUIDField(default=uuid4)

    @property
    def appointments_for_moment(self):
        apps_time: DefaultDict[str, List['Appointment']] = defaultdict(list)
        appointments = Appointment.objects.filter(date=self.date,
                                                  start_time__range=(self.start_time, self.end_time)).order_by(
            'start_time')
        for appointment in appointments:
            apps_time[str(appointment.start_time)[:-3]].append(appointment)
        return apps_time

    def __str__(self) -> str:
        return f'{self.date} van {self.start_time} tot {self.end_time}'


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
        return appointments < self.coursemoment_set.get(course=course).places

    class Meta:
        verbose_name = _("Toetsmoment")
        verbose_name_plural = _("Toetsmomenten")
        unique_together = ['start_time', 'end_time', 'location', 'date']


class CourseMoment(models.Model):
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
