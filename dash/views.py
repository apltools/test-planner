from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request: HttpRequest):
    if request.user.is_staff:
        return HttpResponse("USER IS STAFF!")
    return HttpResponse("Not logged in")
