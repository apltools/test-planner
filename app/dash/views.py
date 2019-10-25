from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from planner.models import TestMoment, AppointmentList
from typing import List, Tuple
# Create your views here.
from django.urls import reverse

@staff_member_required
def index(request: HttpRequest) -> HttpResponse:
    test_moments: List[TestMoment] = TestMoment.objects.all()

    moment_data: List[Tuple[TestMoment, AppointmentList]] = [(moment, moment.appointments_for_moment()) for moment in test_moments]

    context = {
        'moment_data': moment_data
    }

    return render(request, 'dash/index.html', context=context)
