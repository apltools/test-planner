from django.urls import path

from . import views

urlpatterns = [
    path('appointments/<int:test_moment_id>/', views.appointments, name='index'),
    path('appointments/cancel/', views.cancel_appointment, name='cancel_appointment')
]
