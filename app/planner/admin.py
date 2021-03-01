from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, EventType, Event, EventAppointment


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ['username', 'first_name', 'last_name', 'is_staff', 'is_teaching_assistant',]

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_teaching_assistant',)}),
    )

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teaching_assistant',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(EventType)
admin.site.register(EventAppointment)
admin.site.register(Event)
