from django.urls import path

from . import views

app_name = 'dash'
urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history, name='history'),
    path('create_event_type/', views.create_event_type, name='create-event-type'),
    path('create_events/', views.select_event_type, name='create-events'),
    path('create_events/<slug:event_type_slug>/', views.create_events, name='create-events-for'),
]
