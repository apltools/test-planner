from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm, EventForm
from .models import User, EventType, Event, EventAppointment


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('slots', 'slot_length')
    form = EventForm
    list_display = ('event_type', 'date', 'time_string', 'host', 'location', 'slot_length', 'capacity', 'extras')


class EventAppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time_string', 'extras')


admin.site.register(User, CustomUserAdmin)
admin.site.register(EventType)
admin.site.register(EventAppointment, EventAppointmentAdmin)
admin.site.register(Event, EventAdmin)
