from typing import List, Dict, Any

import django.utils.timezone as tz
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from planner.models import Event, EventType
from .forms import CreateEventTypeForm, CreateEventsForm

context: Dict[str, Any] = {
    'nav_items': {
        'Home': 'dash:index',
        'Geschiedenis': 'dash:history',
        'Nieuw EventType': 'dash:create-event-type',
        'Genereer Events': 'dash:create-events',
    }
}


@ensure_csrf_cookie
@staff_member_required
def index(request: HttpRequest) -> HttpResponse:
    events = Event.objects.filter(date__gte=tz.localdate()).order_by('date', 'start_time')

    context.update({
        'events': events
    })

    return render(request, 'dash/index.html', context)


@ensure_csrf_cookie
@staff_member_required
def history(request: HttpRequest) -> HttpResponse:
    events = Event.objects.filter(date__lt=tz.localdate()).order_by('-date', 'start_time')

    context.update({
        'events': events,
    })

    return render(request, 'dash/index.html', context)


def create_event_type(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CreateEventTypeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'EventType added!')
            return redirect('dash:index')
    else:
        form = CreateEventTypeForm()

    context.update({
        'form': form,
    })

    return render(request, 'dash/createEventType.html', context)


def select_event_type(request: HttpRequest) -> HttpResponse:
    event_types = EventType.objects.all()

    context.update({
        'event_types': event_types,
    })

    return render(request, 'dash/selectEventType.html', context)

def create_events(request: HttpRequest, event_type_slug: str) -> HttpResponse:
    try:
        event_type = EventType.objects.get(slug__exact=event_type_slug)

    except EventType.DoesNotExist:
        raise Http404('EventType does not exist')

    if request.method == 'POST':
        form = CreateEventsForm(request.POST)
        form.is_valid()
    else:
        form = CreateEventsForm(initial={
            'slot_length': event_type.slot_length,
            'location': event_type.location,
            'extras': event_type.extras,
            'capacity': event_type.capacity,
            'is_zoom_meeting': event_type.is_zoom_meeting,
        })


    context.update({
        'event_type': event_type,
        'form': form,
    })

    return render(request, 'dash/createEvents.html', context)
