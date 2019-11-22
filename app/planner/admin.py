from django.contrib import admin

from .forms import CourseTimeSlotForm
from .models import User, Course, TestMoment, Test, Appointment, CourseMoment


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseMoment
    extra = 1
    # One of these lines is the better solution :)
    form = CourseTimeSlotForm

class TestMomentAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)
    list_display = ('date','time_string', 'course_name_list')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(User)
admin.site.register(Course, CourseAdmin)
admin.site.register(TestMoment, TestMomentAdmin)
admin.site.register(Test)
admin.site.register(Appointment)
