from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
from django.urls import reverse

from planner.models import Course, Appointment, TestMoment


def send_confirm_email(*, course: Course, appointment: Appointment, test_moment: TestMoment, request: HttpRequest):
    url = request.build_absolute_uri(
        reverse("cancel", kwargs={"course_name": course.short_name, "secret": appointment.cancel_secret}))

    message = f'Je hebt je ingeschreven voor het maken van een toetsje op {_date(appointment.date, "l j F")} ' \
              f'om {_time(appointment.start_time)}.\r\nHet maken van dit toetsje vindt plaats in {test_moment.location}.\r\n' \
              f'Wil je de afspraak anuleren, dat kan via deze link {url}'

    send_mail(subject=f'Toetsje ingepland voor {course.name}',
              message=message,
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[appointment.email])
