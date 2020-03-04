from collections import defaultdict
from locale import _append_modifier
from typing import Dict, Type, Optional
from uuid import UUID

import django.utils.timezone as tz
from django.db import IntegrityError
from django.http import Http404, HttpRequest, HttpResponse, QueryDict
from django.shortcuts import render
from django.utils.translation import gettext as _

from .forms import EventAppointmentForm
from .models import Event, EventType, EventAppointment, add_time
from .mailer import send_confirm_email


def index(request) -> HttpResponse:
    return render(request, 'planner/index.html')


def event_type_index(request: HttpRequest, event_type: str) -> HttpResponse:
    """A page with all events in a EventType"""
    try:
        event_type = EventType.objects.get(slug=event_type)
    except EventType.DoesNotExist:
        raise Http404('Invalid event type')

    events = event_type.events_next_week()

    events_per_date = defaultdict(list)

    # Put events in list per day
    for event in events:
        events_per_date[event.date].append(event)

    # Sort Events within the same day
    for date in events_per_date.values():
        date.sort(key=lambda moment: moment.start_time)

    context = {
        'events_per_date': events_per_date.items(),
        'event_type': event_type,
    }

    return render(request, 'planner/events.html', context=context)


def extract_extras(post: Type[QueryDict], event: Event) -> Optional[dict]:
    if not event.extras:
        return None

    names = [field['name'] for field in event.extras.get('fields')]
    post_dict = dict(post)
    extras = {name: post_dict[name] for name in names}
    return extras


def choose_event(request: HttpRequest, event_type: str, uuid: UUID) -> HttpResponse:
    """View for choosing a time."""

    # Validate EventType
    try:
        event_type = EventType.objects.get(slug__exact=event_type)
    except EventType.DoesNotExist:
        raise Http404('Invalid EventType')

    # Validate Event
    try:
        event = Event.objects.get(uuid__exact=uuid, event_type__exact=event_type)
    except (EventType.DoesNotExist, ValueError):
        raise Http404('Invalid Event UUID')

    if request.method == "POST":
        form = EventAppointmentForm(request.POST, event=event)
        if form.is_valid():
            time = form.cleaned_data['start_time']

            if time not in [slot.time for slot in event.slots]:
                return render(request, 'planner/error.html', context={'error_message': _('Invalid time')}, )

            # Check if slot is open and not in the past
            if not event.slot_open(time=time):
                return render(request, 'planner/error.html', context={'error_message': _("Slot niet beschikbaar.")})

            app: EventAppointment = form.save(commit=False)
            app.date = event.date
            app.end_time = add_time(app.start_time, minutes=event.slot_length())
            app.extras = extract_extras(request.POST, event)
            app.event = event

            try:
                app.save()
            except IntegrityError:
                # Duplicate appointment on day
                return render(request, 'planner/error.html',
                              context={'error_message': _('Je hebt al een afspraak staan voor deze dag.')}, )

            send_confirm_email(event=event, appointment=app, request=request)
            return render(request, 'planner/done.html', context={'app': app, 'event': event})

    else:
        form = EventAppointmentForm(event=event, initial={'date': event.date})

    context = {
        'event_type': event_type,
        'event': event,
        'form': form,
    }

    return render(request, 'planner/times.html', context=context)


def cancel_appointment(request: HttpRequest, event_type: str, secret: str) -> HttpResponse:
    try:
        event_type = EventType.objects.get(slug__exact=event_type)
    except EventType.DoesNotExist:
        raise Http404("Invalid EventType")

    try:
        appointment = EventAppointment.objects.get(cancel_secret__exact=secret)
    except EventAppointment.DoesNotExist:
        return render(request, 'planner/error.html',
                      {'error_message': _('Ongeldige link'),
                       'event_type': event_type})

    if request.method == "POST":
        now = tz.localtime().time()
        today = tz.localdate()

        if appointment.date < today:
            return render(request, 'planner/error.html',
                          {'error_message': _('Deze afspraak ligt in het verleden'),
                           'event_type': event_type})
        elif appointment.date == today:
            if appointment.start_time <= now:
                return render(request, 'planner/error.html',
                              {'error_message': _('Deze afspraak is al gestart of is in het verleden'),
                               'event_type': event_type})
        appointment.delete()

        return render(request, 'planner/error.html', {'error_message': _("Afspraak verwijderd!")})

    return render(request, 'planner/cancel.html')
