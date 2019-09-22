from django.urls import path

from . import views

urlpatterns = [
    path('<slug:course_name>/', views.choose_date, name='choose_date'),
    path('<slug:course_name>/<slug:date>/', views.choose_time, name='choose_time'),
    path('', views.index),
]
