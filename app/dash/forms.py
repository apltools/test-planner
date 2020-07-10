from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.contrib.postgres.forms import JSONField
from django.forms import CheckboxSelectMultiple
from .widgets import BootstrapDatePickerInput, BootstrapTimePickerInput

from planner.models import EventType, Event


class CreateEventTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateEventTypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('create', 'Create'))

    class Meta:
        model = EventType
        fields = [
            'name',
            'slug',
            'hosts',
            'capacity',
            'slot_length',
            'location',
            'extras',
            'is_zoom_meeting'
        ]
        widgets = {
            'hosts': CheckboxSelectMultiple(),
        }

class CreateEventsForm(forms.Form):
    slot_length = forms.DurationField()
    location = forms.CharField()
    extras = JSONField()
    capacity = forms.IntegerField()
    is_zoom_meeting = forms.BooleanField()
    first_date = forms.DateField(widget=BootstrapDatePickerInput())
    last_date = forms.DateField(widget=BootstrapDatePickerInput())

    def __init__(self, *args, **kwargs):
        super(CreateEventsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()


    # class Meta:
    #     model = Event
    #     exclude = ['hosts', 'event_type', 'uuid', 'start_time', 'end_time']
    #     widgets =    {
    #         'date': BootstrapDatePickerInput(),
    #         'start_time': BootstrapTimePickerInput(),
    #         'end_time': BootstrapTimePickerInput(),
    #     }
