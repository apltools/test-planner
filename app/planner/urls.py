from django.urls import path, re_path

from . import views

urlpatterns = [
    path('done/', views.done, name='done'),
    path('<slug:course_name>/', views.choose_date, name='choose_date'),
    re_path(r'^(?P<course_name>[a-zA-Z0-9_-]+)/cancel/(?P<secret>[a-zA-Z0-9]{64})/?$', views.cancel_appointment,
            name='cancel'),
    path('<slug:course_name>/<slug:date>/', views.choose_time, name='choose_time'),
    path('', views.index),
]
