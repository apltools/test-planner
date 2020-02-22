from django.urls import path

from . import views

app_name = 'dash'
urlpatterns = [
    path('', views.index, name='index'),
    path('history', views.history, name='history'),
    path('config', views.config, name='config'),
]
