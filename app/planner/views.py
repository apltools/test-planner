from collections import defaultdict
from uuid import UUID

import django.utils.timezone as tz
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import date as _date, time as _time
from django.urls import reverse
from django.utils.translation import gettext as _

from .forms import AppointmentForm
from .models import Appointment, Course, TestMoment


def index(request) -> HttpResponse:
    return render(request, 'planner/index.html')


def choose_date(request: HttpRequest, course_name: str) -> HttpResponse:
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        raise Http404('Invalid course name')

    test_moments = course.tests_this_week()

    moments_per_date = defaultdict(list)

    for moment in test_moments:
        moments_per_date[moment.date].append(moment)

    for date in moments_per_date.values():
        date.sort(key=lambda moment: moment.start_time)

    context = {
        'moments_per_date': moments_per_date.items(),
        'course': course,
    }

    return render(request, 'planner/dates.html', context=context)


def choose_time(request: HttpRequest, course_name: str, uuid: UUID) -> HttpResponse:
    """View for choosing a time."""

    # Validate course
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        raise Http404('Invalid Course')

    try:
        test_moment = TestMoment.objects.get(uuid__exact=uuid, courses__exact=course)
    except (TestMoment.DoesNotExist, ValueError):
        raise Http404('Invalid uuid')

    # Validate of date isn't in the past.
    if test_moment.date < tz.localdate():
        return render(request, 'planner/error.html',
                      {'error_message': _('Deze datum is inmiddels verlopen.'),
                       'course': course, })

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            # Check if time is full
            if not test_moment.spots_available(form.cleaned_data['start_time'], course):
                return render(request, 'planner/error.html',
                              {'error_message': _('Waarschijnlijk was iemand je voor, dit tijdstip is helaas al vol.'),
                               'course': course, })

            # Check if time is in the past
            today = tz.localdate()
            if test_moment.date == today:
                now = tz.localtime().time()
                if form.cleaned_data['start_time'] <= now:
                    return render(request, 'planner/error.html',
                                  {'error_message': _('Deze tijd mag niet meer gekozen worden.'),
                                   'course': course})

            app = Appointment()
            app.student_name = form.cleaned_data['student_name']
            app.student_nr = form.cleaned_data['student_nr']
            app.email = form.cleaned_data['email']
            app.date = test_moment.date
            app.course = course
            app.start_time = form.cleaned_data["start_time"]
            app.duration = test_moment.test_length

            # Save can go wrong is student had a appointment on this date
            try:
                app.save()
            except IntegrityError:
                return render(request, 'planner/error.html',
                              {'error_message': _('Het maken van een dubbele afspraak op een dag is niet toegestaan.'),
                               'course': course, })

            app.tests.set(form.cleaned_data['tests'])

            send_confirm_email(course=course, appointment=app, test_moment=test_moment, request=request)

            return done(request, course=course, app=app, tm=test_moment)

    else:
        form = AppointmentForm()

    course_moment = test_moment.coursemoment_set.get(course__exact=course)
    # Insert the allowed tests for the course into the form as options.
    form.fields['tests'].queryset = course_moment.allowed_tests.all()

    context = {
        'course': course,
        'test_moment': test_moment,
        'course_moment': course_moment,
        'form': form,
        'student_slots': test_moment.student_slots_for_course(course),
    }

    return render(request, 'planner/times.html', context=context)


def done(request: HttpRequest, *, course: Course, app: Appointment, tm: TestMoment) -> HttpResponse:
    context = {
        'app': app,
        'course': course,
        'tm': tm
    }
    return render(request, 'planner/done.html', context=context)


def send_confirm_email(*, course: Course, appointment: Appointment, test_moment: TestMoment, request: HttpRequest):
    url = request.build_absolute_uri(
        reverse("cancel", kwargs={"course_name": course.short_name, "secret": appointment.cancel_secret}))

    message = _(f'Je hebt je ingeschreven voor het maken van een toetsje op {_date(appointment.date, "l j F")} ' \
              f'om {_time(appointment.start_time)}.\r\nHet maken van dit toetsje vindt plaats in {test_moment.location}.\r\n' \
              f'Wil je de afspraak anuleren, dat kan via deze link {url}')

    if not settings.EMAIL_HOST:
        print(message)
        return
    send_mail(subject=_(f'Toetsje ingepland voor {course.name}'),
              message=message,
              from_email=settings.EMAIL_FROM,
              recipient_list=[appointment.email])


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
