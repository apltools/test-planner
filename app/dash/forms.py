from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from planner.models import EventType
# from django.contrib.postgres.forms import JSONField
from .widgets import BootstrapDatePickerInput


class CreateEventTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateEventTypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('create', 'Create'))

    class Meta:
        model = EventType
        fields = '__all__'


class CreateEventsForm(forms.Form):
    first_date = forms.DateField(widget=BootstrapDatePickerInput())
    last_date = forms.DateField(widget=BootstrapDatePickerInput())

    def __init__(self, *args, **kwargs):
        super(CreateEventsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
