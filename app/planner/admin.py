from django.contrib import admin
# from django.db import models
# from django.forms import CheckboxSelectMultiple
# from django.forms import CheckboxSelectMultiple, ModelForm
from django import forms

from .models import User, Course, TestMoment, Test, Appointment, CourseMoment


class CourseTimeSlotMemberInline(admin.TabularInline):
    model = CourseMoment
    extra = 1


class TestMomentForm(forms.ModelForm):
    class Meta:
        model = TestMoment
        fields = '__all__'
        widgets = {
            'allowed_tests': forms.CheckboxSelectMultiple
        }


class TestMomentAdmin(admin.ModelAdmin):
    inlines = (CourseTimeSlotMemberInline,)
    form = TestMomentForm

    # formfield_overrides = {
    #     models.ManyToManyField: {'widget': CheckboxSelectMultiple}
    # }


admin.site.register(User)
admin.site.register(Course)
admin.site.register(TestMoment, TestMomentAdmin)
admin.site.register(Test)
admin.site.register(Appointment)
