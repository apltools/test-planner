from typing import List

import django.utils.timezone as tz
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from dash.forms import EventTypeCreateForm, EventCreateForm, ChooseEventTypeForm
from planner.models import Event, EventType

nav_items = {
    'Home': 'dash:index',
    'Geschiedenis': 'dash:history',
    'Nieuw EventType': 'dash:create-event-type',
    'Nieuw Event': 'dash:create-event',
}


@ensure_csrf_cookie
@staff_member_required
def index(request: HttpRequest) -> HttpResponse:
    events: List[Event] = Event.objects.filter(date__gte=tz.localdate()).order_by('date', '_start_time')

    context = {'events': events,
               'nav_items': nav_items}

    return render(request, 'dash/index.html', context=context)


@ensure_csrf_cookie
@staff_member_required
def history(request: HttpRequest) -> HttpResponse:
    events: List[Event] = Event.objects.filter(date__lt=tz.localdate()).order_by('-date', 'start_time')
    context = {'events': events,
               'nav_items': nav_items}

    return render(request, 'dash/index.html', context=context)

@staff_member_required
def create_event_type(request: HttpRequest) -> HttpResponse:
    event_types = EventType.objects.all()

    event_type_form = EventTypeCreateForm()

    if request.method == 'POST':
        event_type_form = EventTypeCreateForm(request.POST)
        if event_type_form.is_valid():
            event_type_form.save()


    context = {
        'event_types': event_types,

        'form': event_type_form,
    }
    return render(request, 'dash/createEventType.html', context)

def create_event(request: HttpRequest) -> HttpRequest:
    form = ChooseEventTypeForm()

    context = {
        'form': form,
    }
    return render(request, 'dash/createEvent.html', context)