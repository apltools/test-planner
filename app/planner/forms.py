from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Event, User, EventAppointment


def mod11(nr: int):
    mod11_sum = 0

    for i, digit in enumerate(reversed(str(nr))):
        mod11_sum += (i + 1) * int(digit)

    return mod11_sum % 11 == 0


class CheckBoxSelectMultipleBootstrap(forms.CheckboxSelectMultiple):
    template_name = 'planner/forms/widgets/multiple_input.html'
    option_template_name = 'planner/forms/widgets/checkbox_option.html'


class EventAppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.INPUT_TYPES = {'checkbox': EventAppointmentForm.construct_checkbox,
                            'radio': EventAppointmentForm.construct_radio}
        self.checkbox_max_amount = {}
        self.event = kwargs.pop("event")

        if extras := self.event.extras:
            fields = extras.get("fields")
        else:
            fields = None

        super().__init__(*args, **kwargs)

        if fields:
            self.add_extra_fields(fields)

    def clean(self):
        cleaned_data = self.cleaned_data

        for field_name, max_amount in self.checkbox_max_amount.items():
            if len(cleaned_data.get(field_name, [])) > max_amount:
                self.add_error(field_name, f'Kies maximaal {max_amount} opties.')

        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data['name']
        if not ' ' in name:
            raise ValidationError(_('Geef alsjeblieft je voor- en achtenaam op.'), code='no_last_name')
        return name

    def clean_student_nr(self):
        student_nr = self.cleaned_data['student_nr']
        length = len(str(student_nr))

        if length > 8 or length < 7:
            raise ValidationError(_('Ongeldig Studentnummer.'), code='length')
        if not mod11(student_nr):
            raise ValidationError(_('Ongeldig Studentnummer.'), code="mod11")
        return student_nr

    def add_extra_fields(self, fields):
        for field in fields:
            if (type := field.get('type')) not in self.INPUT_TYPES:
                raise EventAppointmentForm.UnsupportedFieldTypeException

            input_field = self.INPUT_TYPES[type](field)

            name = field.get('name')

            # remember max amount
            if (max_amount := field.get('max_amount')):
                self.checkbox_max_amount[name] = max_amount

            self.fields[name] = input_field

    @staticmethod
    def construct_checkbox(field):
        choices = [(item, item) for item in field['options']]
        required = field.get('required', False)
        return forms.MultipleChoiceField(label=field['name'], widget=CheckBoxSelectMultipleBootstrap(), choices=choices,
                                         required=required)

    @staticmethod
    def construct_radio(field):
        choices = [(item, item) for item in field['options']]
        required = field.get('required', False)
        return forms.ChoiceField(label=field['name'], widget=forms.RadioSelect(), choices=choices, required=required)

    class Meta:
        model = EventAppointment
        fields = ('name', 'student_nr', 'email', 'start_time')
        widgets = {
            'name': forms.TextInput(attrs={
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

        labels = {
            'name': _('Voor- en achtenaam'),
        }

        error_messages = {
            'student_nr': {
                'invalid': "Ongeldig studentnummer.",
                'mod11': "ELFPROEF"
            },
            'start_time': {
                'required': "Kies een tijd."
            },
        }

    class UnsupportedFieldTypeException(Exception):
        pass


class EventForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data['event_type']._slot_length and not cleaned_data['_slot_length']:
            raise ValidationError('No length was provided')
        elif not cleaned_data['event_type']._location and not cleaned_data['_location']:
            raise ValidationError('No locations was provided')
        print(f"{cleaned_data=}")
        return cleaned_data

    class Meta:
        exclude = ('',)
        model = Event


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
