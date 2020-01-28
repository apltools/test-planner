from django.urls import path, re_path

from . import views

urlpatterns = [
    path('done/', views.done, name='done'),
    path('<slug:event_type>/', views.event_type_index, name='event_type_index'),
    re_path(r'^(?P<course_name>[a-zA-Z0-9_-]+)/cancel/(?P<secret>[a-zA-Z0-9]{64})/?$', views.cancel_appointment,
            name='cancel'),
    path('<slug:event_type>/<uuid:uuid>/', views.choose_event, name='choose-event'),
    path('', views.index),
]
