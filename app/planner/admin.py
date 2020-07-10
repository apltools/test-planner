from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import EventForm
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

class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('slots', 'slot_length')
    form = EventForm
    # list_display = ('event_type', 'date', , 'extras')


class EventAppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time_string', 'extras')


admin.site.register(User, CustomUserAdmin)
admin.site.register(EventType)
admin.site.register(EventAppointment, EventAppointmentAdmin)
admin.site.register(Event, EventAdmin)
