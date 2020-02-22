from django.urls import path

from . import views

urlpatterns = [
    path('appointments/<int:event_id>/', views.appointments, name='index'),
    path('appointments/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('tests/', views.tests_for_student),
]
