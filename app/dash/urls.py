from django.urls import path

from . import views

app_name = 'dash'
urlpatterns = [
    path('', views.index, name='index'),
    path('history', views.history, name='history'),
    path('create_event_type/', views.create_event_type, name='create-event-type'),
    path('create_event/', views.create_event, name='create-event'),
]
