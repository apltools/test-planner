from collections import defaultdict
from typing import Dict, Type
from uuid import UUID

import django.utils.timezone as tz
from django.http import Http404, HttpRequest, HttpResponse, QueryDict
from django.shortcuts import render
from django.utils.translation import gettext as _

from .forms import AppointmentForm, EventAppointmentForm
from .models import Appointment, Course, Event, EventType, TestMoment, EventAppointment, add_time


def index(request) -> HttpResponse:
    return render(request, 'planner/index.html')


def event_type_index(request: HttpRequest, event_type: str) -> HttpResponse:
    """A page with all events in a EventType"""
    try:
        event_type = EventType.objects.get(slug=event_type)
    except EventType.DoesNotExist:
        raise Http404('Invalid event type')

    # TODO: Don't return all events
    events = event_type.events.all()

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


def extract_extras(post: Type[QueryDict], event: Event) -> Dict:
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

    # Validate of date isn't in the past.
    # if event.date < tz.localdate():
    #     return render(request, 'planner/error.html',
    #                   {'error_message': _('Deze datum is inmiddels verlopen.'),
    #                    'course': course, })

    if request.method == "POST":
        # TODO: Check is slot if full and is slot isn't closed
        form = EventAppointmentForm(request.POST, event=event)
        if form.is_valid():
            app: EventAppointment = form.save(commit=False)
            app.date = event.date
            app.end_time = add_time(app.start_time, minutes=event.slot_length())
            app.extras = extract_extras(request.POST, event)
            app.save()

            return render(request, 'planner/done.html', context={'app': app, 'event': event})

    # if form.is_valid():
    #     # Check if time is full
    #     if not test_moment.spots_available(form.cleaned_data['start_time'], course):
    #         return render(request, 'planner/error.html',
    #                       {'error_message': _('Waarschijnlijk was iemand je voor, dit tijdstip is helaas al vol.'),
    #                        'course': course, })
    #
    #     # Check if time is in the past
    #     today = tz.localdate()
    #     if test_moment.date == today:
    #         now = tz.localtime().time()
    #         if form.cleaned_data['start_time'] <= now:
    #             return render(request, 'planner/error.html',
    #                           {'error_message': _('Deze tijd mag niet meer gekozen worden.'),
    #                            'course': course})
    #
    #     app = Appointment()
    #     app.student_name = form.cleaned_data['student_name']
    #     app.student_nr = form.cleaned_data['student_nr']
    #     app.email = form.cleaned_data['email']
    #     app.date = test_moment.date
    #     app.course = course
    #     app.start_time = form.cleaned_data["start_time"]
    #     app.duration = test_moment.test_length
    #
    #     # Save can go wrong is student had a appointment on this date
    #     try:
    #         app.save()
    #     except IntegrityError:
    #         return render(request, 'planner/error.html',
    #                       {'error_message': _('Het maken van een dubbele afspraak op een dag is niet toegestaan.'),
    #                        'course': course, })
    #
    #     app.tests.set(form.cleaned_data['tests'])
    #
    #     send_confirm_email(course=course, appointment=app, test_moment=test_moment, request=request)
    #
    #     return done(request, course=course, app=app, tm=test_moment)

    else:
        form = EventAppointmentForm(event=event, initial={'date': event.date})

    context = {
        'event_type': event_type,
        'event': event,
        'form': form,
    }

    return render(request, 'planner/times.html', context=context)


def done(request: HttpRequest, *, course: Course, app: Appointment, tm: TestMoment) -> HttpResponse:
    context = {
        'app': app,
        'course': course,
        'tm': tm
    }
    return render(request, 'planner/done.html', context=context)


def cancel_appointment(request: HttpRequest, course_name: str, secret: str) -> HttpResponse:
    try:
        course = Course.objects.get(short_name__exact=course_name)
    except Course.DoesNotExist:
        raise Http404("Invalid Course")

    try:
        appointment = Appointment.objects.get(cancel_secret__exact=secret, course__exact=course)
    except Appointment.DoesNotExist:
        return render(request, 'planner/error.html',
                      {'error_message': _('Ongeldige link'),
                       'course': course})

    if request.method == "POST":
        now = tz.localtime().time()
        today = tz.localdate()

        if appointment.date < today:
            return render(request, 'planner/error.html',
                          {'error_message': _('Dit toetsje is in het verleden'),
                           'course': course})
        elif appointment.date == today:
            if appointment.start_time <= now:
                return render(request, 'planner/error.html',
                              {'error_message': _('Dit toetsje is al gestart of is in het verleden'),
                               'course': course})
        appointment.delete()

        return render(request, 'planner/error.html', {'error_message': _("Afspraak verwijderd!")})

    return render(request, 'planner/cancel.html', {'course': course})
