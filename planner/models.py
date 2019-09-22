from datetime import timedelta, datetime, date

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


class TimeSlot(models.Model):
    location = models.fields.CharField(max_length=16)  # Own model with capacity?
    date = models.fields.DateField()
    start_time = models.fields.TimeField()
    end_time = models.fields.TimeField()
    slot_length = models.fields.IntegerField()
    hidden_from_total = models.fields.BooleanField(default=False)

    courses = models.ManyToManyField(Course, through='CourseTimeSlotMember', related_name='timeslots')

    @property
    def slot_delta(self) -> timedelta:
        return timedelta(minutes=self.slot_length)

    @property
    def student_slots(self):
        cur_time = datetime.combine(date.today(), self.start_time)
        end_time = datetime.combine(date.today(), self.end_time)

        slots = []

        while cur_time + self.slot_delta <= end_time:
            slots.append(cur_time.time())
            cur_time = cur_time + self.slot_delta

        return slots


class CourseTimeSlotMember(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    places = models.fields.IntegerField()


class Test(models.Model):
    name = models.fields.CharField(max_length=32)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    student_name = models.fields.CharField(max_length=32, verbose_name="Name")
    email = models.fields.EmailField(verbose_name="E-mail")
    date = models.fields.DateField()
    time = models.fields.TimeField()
    duration = models.fields.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    tests = models.ManyToManyField(Test)

    def __str__(self):
        return f'{self.student_name} om {self.time} op {self.date}'

    class Meta:
        unique_together = ('email', 'date')
        verbose_name = _("Appointment")
        verbose_name_plural = _("Appointments")

