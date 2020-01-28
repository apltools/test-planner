from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CourseTimeSlotForm, CustomUserChangeForm, CustomUserCreationForm, EventForm
from .models import Appointment, Course, CourseMomentRelation, Test, TestMoment, User, EventType, Event,EventAppointment


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseMomentRelation
    extra = 1
    # One of these lines is the better solution :)
    form = CourseTimeSlotForm


class TestMomentAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)
    list_display = ('date', 'time_string', 'course_name_list')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

class EventAdmin(admin.ModelAdmin):
    readonly_fields = ['slots', 'slot_length']
    form = EventForm
    list_display = ['event_type', 'date', 'time_string', 'host', 'location', 'slot_length', 'extras']


admin.site.register(User, CustomUserAdmin)
admin.site.register(EventType)
admin.site.register(EventAppointment)
admin.site.register(Event, EventAdmin)

# admin.site.register(Course, CourseAdmin)
# admin.site.register(TestMoment, TestMomentAdmin)
# admin.site.register(Test)
# admin.site.register(Appointment)
