from django.contrib import admin

from .models import User, Course, TestMoment, Test, Appointment, CourseMoment


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseMoment
    extra = 1


class TimeSlotAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)


admin.site.register(User)
admin.site.register(Course)
admin.site.register(TestMoment, TimeSlotAdmin)
admin.site.register(Test)
admin.site.register(Appointment)
