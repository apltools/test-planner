import datetime

from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render

from .forms import AppointmentForm
from .models import Course, TimeSlot, Appointment


def index(request):
    return render(request, 'planner/dates.html')


def choose_date(request: HttpRequest, course_name: str) -> HttpResponse:
    try:
        course = Course.objects.get(short_name=course_name)
    except Course.DoesNotExist:
        return HttpResponseNotFound("Invalid course name")

    tss = course.timeslots.all()
    dates = tss.values_list('date', flat=True)

    context = {
        'tss': tss,
        'dates': dates,
        'course': course
    }

    return render(request, 'planner/dates.html', context=context)


def choose_time(request: HttpRequest, course_name: str, date: str) -> HttpResponse:
    course = Course.objects.get(short_name=course_name)
    date_obj = datetime.date.fromisoformat(date)
    ts = TimeSlot.objects.get(date=date_obj)

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
                return HttpResponseForbidden()

    else:
        form = AppointmentForm(initial={
            'date': date_obj,
            'course': course,
            'duration': ts.slot_length,
        },)

    context = {
        'course': course,
        'ts': ts,
        'form': form
    }

    return render(request, 'planner/times.html', context=context)
