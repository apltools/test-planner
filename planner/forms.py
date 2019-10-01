import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Appointment


class CheckBoxSelectMultipleBootstrap(forms.CheckboxSelectMultiple):
    template_name = 'planner/forms/widgets/multiple_input.html'
    option_template_name = 'planner/forms/widgets/checkbox_option.html'


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = ['student_name', 'email', 'tests', 'duration']
        widgets = {
            'tests': CheckBoxSelectMultipleBootstrap(),
            'student_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'duration': forms.HiddenInput(),
        }
        error_messages = {
            'tests': {
                'required': "Kies minimaal één toetsje."
            },
        }
