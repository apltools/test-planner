from typing import List

import django.utils.timezone as tz
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from planner.models import TestMoment

nav_items = {
    'Home': 'dash:index',
    'Geschiedenis': 'dash:history',
}


@ensure_csrf_cookie
@staff_member_required
def index(request: HttpRequest) -> HttpResponse:
    test_moments: List[TestMoment] = TestMoment.objects.filter(date__gte=tz.localdate()).order_by('date', 'start_time')

    context = {'test_moments': test_moments,
               'nav_items': nav_items}

    return render(request, 'dash/index.html', context=context)


@ensure_csrf_cookie
@staff_member_required
def history(request: HttpRequest) -> HttpResponse:
    test_moments: List[TestMoment] = TestMoment.objects.filter(date__lt=tz.localdate()).order_by('-date', 'start_time')
    context = {'test_moments': test_moments,
               'nav_items': nav_items}

    return render(request, 'dash/index.html', context=context)
