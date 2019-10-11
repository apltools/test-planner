from django.contrib import admin
# from django.db import models
# from django.forms import CheckboxSelectMultiple
# from django.forms import CheckboxSelectMultiple, ModelForm
from django import forms

from .models import User, Course, TestMoment, Test, Appointment, CourseMoment


class CourseTimeSlotForm(forms.ModelForm):
    class Meta:
        model = CourseMoment
        fields = '__all__'
        widgets = {
            'allowed_tests': forms.CheckboxSelectMultiple
        }


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseMoment
    extra = 1
    form = CourseTimeSlotForm


class TestMomentAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)



admin.site.register(User)
admin.site.register(Course)
admin.site.register(TestMoment, TestMomentAdmin)
admin.site.register(Test)
admin.site.register(Appointment)
