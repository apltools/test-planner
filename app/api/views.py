import datetime as dt
from collections import defaultdict

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.models import model_to_dict
from django.http import HttpRequest, JsonResponse
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time

from api.decorators import staff_member_required_json
from planner.models import EventAppointment, Event




class EventAppointmentsEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, EventAppointment):
            obj_dict = model_to_dict(obj, fields=['name', 'extras', 'id'])
            return obj_dict

        elif isinstance(obj, Event):
            obj_dict = model_to_dict(obj, fields=('date'))
            obj_dict['name'] = obj.event_type.name
            return obj_dict

        elif isinstance(obj, dt.date):
            return _date(obj, "l j F").capitalize()

        elif isinstance(obj, models.Model):
            return model_to_dict(obj)

        return super().default(obj)


@staff_member_required_json
def appointments(request: HttpRequest, event_id) -> JsonResponse:
    event = Event.objects.get(id__exact=event_id)
    apps = list(event.appointments.all())
    apps_per_slot = defaultdict(list)
    for app in apps:
        apps_per_slot[_time(app.start_time)].append(app)

    return JsonResponse({'event': event, 'appointments': apps_per_slot}, encoder=EventAppointmentsEncoder, safe=False)


@staff_member_required_json
def cancel_appointment(request: HttpRequest) -> JsonResponse:
    try:
        app_id = int(request.POST.get('appId'))
        EventAppointment.objects.get(id__exact=app_id).delete()
    except Exception as e:
        print(e)
        return JsonResponse(False, safe=False)
    return JsonResponse(True, safe=False)

# TODO: Endpoint, geeft studentnummer en wil toetsjes terug
