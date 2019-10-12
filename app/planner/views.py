import datetime

from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

from .forms import AppointmentForm
from .models import Course, TestMoment, Appointment


def index(request):
    return render(request, 'planner/index.html')


def choose_date(request: HttpRequest, course_name: str) -> HttpResponse:
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        raise Http404("Invalid course name")

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
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        raise Http404("Invalid Course")

    try:
        date_obj = datetime.date.fromisoformat(date)
        test_moment = TestMoment.objects.get(date=date_obj)
    except (TestMoment.DoesNotExist, ValueError):
        raise Http404("Invalid date")

    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            app = Appointment()
            app.student_name = form.cleaned_data['student_name']
            app.student_nr = form.cleaned_data['student_nr']
            app.email = form.cleaned_data['email']
            app.date = date_obj
            app.course = course
            app.start_time = form.data["start_time"]
            app.duration = test_moment.test_length

            try:
                app.save()
            except IntegrityError:
                raise Http404("Duplicate appointment on date is not allowed")

            app.tests.set(form.cleaned_data['tests'])
            return render(request, 'planner/done.html')

    else:
        # Config for fresh form.
        form = AppointmentForm(initial={
            'date': date_obj,
            'course': course,
        })

    form.fields['tests'].queryset = test_moment.coursemoment_set.get(course__exact=course).allowed_tests.all()

    context = {
        'course': course,
        'ts': test_moment,
        'form': form,
        'student_slots': test_moment.student_slots_for_course(course),
    }

    return render(request, 'planner/times.html', context=context)
