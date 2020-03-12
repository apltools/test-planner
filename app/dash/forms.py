from crispy_forms.layout import Submit, Button
from django import forms

from planner.models import EventType, Event

from crispy_forms.helper import FormHelper


class EventTypeCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EventTypeCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))


    class Meta:
            fields = ['name', '_host', '_slot_length', '_capacity', 'slug']
            model = EventType

class ChooseEventTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChooseEventTypeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Button('select-type', 'Volgende', css_class='btn-primary', ))

    class Meta:
        model = Event
        fields = ('event_type',)

class EventCreateForm(forms.ModelForm):

    class Meta:
        fields = '__all__'
        model = Event