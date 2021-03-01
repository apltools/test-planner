import datetime as dt

from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _


def add_time(time: dt.time, *, hours: int = 0, minutes: int = 0) -> dt.time:
    return (dt.datetime.combine(dt.date.today(), time) + dt.timedelta(hours=hours, minutes=minutes)).time()


def subtract_time(time: dt.time, *, hours: int = 0, minutes: int = 0) -> dt.time:
    return (dt.datetime.combine(dt.date.today(), time) - dt.timedelta(hours=hours, minutes=minutes)).time()


def diff_time(time1: dt.time, time2: dt.time) -> dt.timedelta:
    return dt.datetime.combine(dt.date.today(), time1) - dt.datetime.combine(dt.date.today(), time2)


def gen_cancel_secret(length: int = 64) -> str:
    return get_random_string(length=length)


def validate_timeslot(value):
    if 60 % value != 0:
        raise ValidationError(_('%(value)s is not divisible by 60.'), params={'value': value})
