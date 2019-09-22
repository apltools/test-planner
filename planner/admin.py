from django.contrib import admin

from .models import User, Course, TimeSlot, Test, Appointment, CourseTimeSlotMember


# Register your models here.


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseTimeSlotMember
    extra = 1


class TimeSlotAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)
    # readonly_fields =


admin.site.register(User)
admin.site.register(Course)
admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Test)
admin.site.register(Appointment)
