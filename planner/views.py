import datetime

from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render

from .forms import AppointmentForm
from .models import Course, TestMoment, Appointment


def index(request):
    return render(request, 'planner/dates.html')


def choose_date(request: HttpRequest, course_name: str) -> HttpResponse:
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        return HttpResponseNotFound("Invalid course name")

    test_moments = course.tests_this_week()
    dates = test_moments.values_list('date', flat=True)

    context = {
        'test_moments': test_moments,
        'dates': dates,
        'course': course
    }

    return render(request, 'planner/dates.html', context=context)


def choose_time(request: HttpRequest, course_name: str, date: str) -> HttpResponse:
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        return HttpResponseNotFound("Invalid Course")

    try:
        date_obj = datetime.date.fromisoformat(date)
        ts = TestMoment.objects.get(date=date_obj)
    except (TestMoment.DoesNotExist, ValueError):
        return HttpResponseNotFound("Invalid date")

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            app = Appointment()
            app.student_name = form.cleaned_data['student_name']
            app.email = form.cleaned_data['email']
            app.date = date_obj
            app.course = course
            app.start_time = form.data["start_time"]
            app.duration = form.data["duration"]
            try:
                app.save()
                app.tests.set(form.cleaned_data['tests'])
                return render(request, 'planner/done.html')
            except IntegrityError:
                return HttpResponseForbidden("Duplicate appointment on date is not allowed")

    else:
        form = AppointmentForm(initial={
            'date': date_obj,
            'course': course,
            'duration': ts.test_length,
        }, )

    context = {
        'course': course,
        'ts': ts,
        'form': form,
        'student_slots': ts.student_slots_for_course(course),
    }

    return render(request, 'planner/times.html', context=context)
