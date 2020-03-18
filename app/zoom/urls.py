from django.urls import path

from . import views

app_name = 'zoom'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('unlink', views.unlink, name='unlink'),
    path('authorize', views.authorize, name='authorize'),
    path('meetings', views.meetings),
]

