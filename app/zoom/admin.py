from django.contrib import admin
from .models import OAuth2Token, ZoomMeeting
# Register your models here.

admin.site.register(OAuth2Token)
admin.site.register(ZoomMeeting)
