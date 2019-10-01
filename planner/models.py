import random
from datetime import timedelta, datetime, date, time

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

class User(AbstractUser):
    pass


class Course(models.Model):
    name = models.fields.CharField(max_length=64)
    short_name = models.fields.SlugField(max_length=16)

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name = _("Vak")
        verbose_name_plural = _("Vakken")


class TimeSlot(models.Model):
    location = models.fields.CharField(max_length=16, verbose_name=_("Locatie"))  # Own model with capacity?
    date = models.fields.DateField(verbose_name=_("Datum"))
    start_time = models.fields.TimeField(verbose_name=_("Begintijd"))
    end_time = models.fields.TimeField(verbose_name=_("Eindtijd"))
    test_length = models.fields.IntegerField(verbose_name=_("Toetslengte"), default=15)
    hidden_from_total = models.fields.BooleanField(default=False)

    courses = models.ManyToManyField(Course, through='CourseTimeSlotMember', related_name='timeslots', verbose_name=_("Vakken"))

    def __str__(self):
        return f'{self.date} van {self.start_time} tot {self.end_time}'

    @property
    def slot_delta(self) -> timedelta:
        """Slot length as a timedelta"""
        return timedelta(minutes=self.test_length)

    @property
    def student_slots(self):
        """List of possible time slots."""
        cur_time = datetime.combine(date.today(), self.start_time)
        end_time = datetime.combine(date.today(), self.end_time)

        slots = []

        while cur_time + self.slot_delta <= end_time:
            slots.append(TimeOption(cur_time.time()))
            cur_time = cur_time + self.slot_delta

        return slots

    class Meta:
        verbose_name = _("Tijdslot")
        verbose_name_plural = _("Tijdslots")

class TimeOption:

    def __init__(self, time: datetime.time, available: bool = True):
        self.time: datetime.time = time
        # self.available: bool = available
        self.available:bool = bool(random.getrandbits(1))
    class Meta:
        managed = False

class CourseTimeSlotMember(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("Vak"))
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name=_("Tijdsslot"))

    places = models.fields.IntegerField(verbose_name=_("Plekken"))


class Test(models.Model):
    name = models.fields.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Toetsje")
        verbose_name_plural = _("Toetsjes")


class Appointment(models.Model):
    student_name = models.fields.CharField(max_length=32, verbose_name=_("Naam"))
    email = models.fields.EmailField(verbose_name=_("E-mail"))
    date = models.fields.DateField(verbose_name=_("Datum"))
    start_time = models.fields.TimeField(verbose_name=_("Begintijd"))
    duration = models.fields.IntegerField(verbose_name=_("Lengte"))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_("Vak"))

    tests = models.ManyToManyField(Test, verbose_name=_("Toetsjes"))

    @property
    def end_time(self) -> time:
        return (datetime.combine(date.today(), self.start_time) + timedelta(minutes=self.duration)).time()

    def __str__(self):
        return f'{self.student_name} om {self.start_time} op {self.date}'

    class Meta:
        unique_together = ('email', 'date')
        verbose_name = _("Afspraak")
        verbose_name_plural = _("Afspraken")

