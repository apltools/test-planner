from typing import Dict, Any

import django.utils.timezone as tz
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from planner.models import Event, EventType, User
from .forms import CreateEventTypeForm, CreateEventsForm

context: Dict[str, Any] = {
    'nav_items': {
        _('Home'): 'dash:index',
        _('History'): 'dash:history',
        _('New Eventtype'): 'dash:create-event-type',
        _('Generate Events'): 'dash:create-events',
    }
}

TIMES = ["9:00",
         "10:00",
         "11:00",
         "12:00",
         "13:00",
         "14:00",
         "15:00",
         "16:00"
         ]

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


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
        print(request.POST)
        form = CreateEventsForm(request.POST)
        form.is_valid()
    else:
        form = CreateEventsForm()

    hosts = User.objects.filter(is_teaching_assistant=True)
    max_nr = 4

    context.update({
        'event_type': event_type,
        'form': form,
        'times': TIMES,
        'hosts': hosts,
        'days': DAYS,
        'nrs': range(max_nr),
    })

    return render(request, 'dash/createEvents.html', context)
