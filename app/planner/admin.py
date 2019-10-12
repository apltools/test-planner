from django.contrib import admin

from .forms import CourseTimeSlotForm
from .models import User, Course, TestMoment, Test, Appointment, CourseMoment


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseMoment
    extra = 1
    form = CourseTimeSlotForm
    # filter_horizontal  = ('allowed_tests',)


class TestMomentAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)


admin.site.register(User)
admin.site.register(Course)
admin.site.register(TestMoment, TestMomentAdmin)
admin.site.register(Test)
admin.site.register(Appointment)
