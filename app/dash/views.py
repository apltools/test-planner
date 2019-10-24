from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from planner.models import Appointment, TestMoment
# Create your views here.
from django.urls import reverse

@staff_member_required
def index(request: HttpRequest):
    test_moments = TestMoment.objects.all()

    moment_data = []

    for moment in test_moments:
        moment_data.append((moment, moment.appointments_for_moment().items()))

    print(moment_data)
    context = {
        'moment_data': moment_data
    }

    return render(request, 'dash/index.html', context=context)
