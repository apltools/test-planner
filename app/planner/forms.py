from django import forms

from .models import Appointment


class CheckBoxSelectMultipleBootstrap(forms.CheckboxSelectMultiple):
    template_name = 'planner/forms/widgets/multiple_input.html'
    option_template_name = 'planner/forms/widgets/checkbox_option.html'


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['student_name','student_nr', 'email', 'tests', 'start_time',]
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
                'required': "Kies minimaal één toetsje."
            },
            'start_time': {
                'required': "Kies een tijd"
            },
            'student_nr': {
                'invalid': "Ongeldig studentnummer"
            },
        }
