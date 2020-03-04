from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
from django.urls import reverse

from planner.models import Event, EventAppointment


def send_confirm_email(*, event: Event, appointment: EventAppointment, request: HttpRequest):
    url = request.build_absolute_uri(
        reverse("cancel", kwargs={"event_type": event.event_type.slug, "secret": appointment.cancel_secret}))

    message = f'Je hebt je ingeschreven voor een afspraak op {_date(appointment.date, "l j F")} ' \
              f'om {_time(appointment.start_time)}.\r\nDe afspraak is in {event.location()}.\r\n' \
              f'Wil je de afspraak anuleren, dat kan via deze link {url}'

    send_mail(subject=f'Afspraak gemaakt voor {event.event_type.name}',
              message=message,
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[appointment.email])
