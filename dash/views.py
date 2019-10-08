from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

@staff_member_required
def index(request: HttpRequest):
    return render(request, 'dash/index.html')
