import datetime as dt

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import date as _date, time as _time
from django.urls import reverse

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
    dates = test_moments.values_list('date', flat=True)

    context = {
        'test_moments': test_moments,
        'dates': dates,
        'course': course
    }

    return render(request, 'planner/dates.html', context=context)


def choose_time(request: HttpRequest, course_name: str, date: str) -> HttpResponse:
    """View for choosing a time."""

    # Validate course
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        raise Http404('Invalid Course')

    # Validate date
    try:
        date_obj = dt.date.fromisoformat(date)
        test_moment = TestMoment.objects.get(date=date_obj)
    except (TestMoment.DoesNotExist, ValueError):
        raise Http404('Invalid date')

    # Validate of date isn't in the future.
    if test_moment.date <= dt.date.today():
        return render(request, 'planner/error.html',
                      {'error_message': 'Deze datum is inmiddels verlopen.',
                       'course': course, })

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            if not test_moment.time_available(form.cleaned_data['start_time'], course):
                return render(request, 'planner/error.html',
                              {'error_message': 'Waarschijnlijk was iemand je voor, dit tijdstip is helaas al vol.',
                               'course': course, })

            app = Appointment()
            app.student_name = form.cleaned_data['student_name']
            app.student_nr = form.cleaned_data['student_nr']
            app.email = form.cleaned_data['email']
            app.date = date_obj
            app.course = course
            app.start_time = form.cleaned_data["start_time"]
            app.duration = test_moment.test_length

            # Save can go wrong is student had a appoitment on this date
            try:
                app.save()
            except IntegrityError:
                return render(request, 'planner/error.html',
                              {'error_message': 'Het maken van een dubbele afspraak op een dag is niet toegestaan.',
                               'course': course, })

            app.tests.set(form.cleaned_data['tests'])

            send_confirm_email(course=course, appointment=app, test_moment=test_moment, request=request)

            return done(request, course=course, app=app, tm=test_moment)

    else:
        form = AppointmentForm()

    # Insert the allowed tests for the course into the form as options.
    form.fields['tests'].queryset = test_moment.coursemoment_set.get(course__exact=course).allowed_tests.all()

    context = {
        'course': course,
        'test_moment': test_moment,
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

    message = f'Je hebt je ingeschreven voor het maken van een toetsje op {_date(appointment.date, "l j F")} ' \
              f'om {_time(appointment.start_time)}.\r\nHet maken van dit toetsje vind plaats in {test_moment.location}.\r\n' \
              f'Wil de de afspraak anuleren, dat kan via deze link {url}'

    if not settings.EMAIL_HOST:
        print(message)
        return
    send_mail(subject=f'Toetsje ingepland voor {course.name}',
              message=message,
              from_email=settings.EMAIL_FROM,
              recipient_list=[appointment.email])


def cancel_appointment(request: HttpRequest, course_name: str, secret: str):
    try:
        course = Course.objects.get(short_name__exact=course_name)
    except Course.DoesNotExist:
        raise Http404("Invalid Course")
    try:
        Appointment.objects.get(cancel_secret__exact=secret, course__exact=course).delete()
    except Appointment.DoesNotExist:
        return render(request, 'planner/error.html',
                      {'error_message': 'Ongeldige link',
                       'course': course})
