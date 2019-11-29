from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import Appointment, CourseMoment, TestMoment, User


class CourseTimeSlotForm(forms.ModelForm):
    class Meta:
        model = CourseMoment
        fields = '__all__'
        widgets = {
            'allowed_tests': forms.CheckboxSelectMultiple
        }


class CheckBoxSelectMultipleBootstrap(forms.CheckboxSelectMultiple):
    template_name = 'planner/forms/widgets/multiple_input.html'
    option_template_name = 'planner/forms/widgets/checkbox_option.html'


class AppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.test_moment: TestMoment = kwargs.pop("test_moment", None)
        super().__init__(*args, **kwargs)

    def clean_tests(self):
        cleaned_data = self.cleaned_data

        if self.test_moment and len(cleaned_data['tests']) > self.test_moment.max_tests:
            raise ValidationError(f"Kies maximaal {self.test_moment.max_tests} toetsjes.", code='invalid_test_amount')

        return cleaned_data

    class Meta:
        model = Appointment
        fields = ['student_name', 'student_nr', 'email', 'tests', 'start_time', ]
        widgets = {
            'tests': CheckBoxSelectMultipleBootstrap(),
            'student_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'student_nr': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'start_time': forms.HiddenInput(),
        }

        error_messages = {
            'tests': {
                'required': "Kies minimaal één toetsje.",
            },
            'start_time': {
                'required': "Kies een tijd"
            },
            'student_nr': {
                'invalid': "Ongeldig studentnummer"
            },
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')
