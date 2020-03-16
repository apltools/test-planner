from django.urls import path

from . import views

app_name = 'zoom'
urlpatterns = [
    path('login', views.login, name='login'),
    path('authorize', views.authorize, name='authorize'),
    path('meetings', views.meetings),
]
