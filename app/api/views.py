import datetime as dt
from collections import defaultdict
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.models import model_to_dict
from django.http import HttpRequest, JsonResponse
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
import datetime as dt
import django.utils.timezone as tz
from django.views.decorators.csrf import csrf_exempt

from api.models import APIKey
from planner.models import EventAppointment, Event


def staff_member_required_json(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return JsonResponse([], safe=False, status=401)

    return wrapped_view

def api_key_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        api_key = APIKey.load().key
        if request.POST.get('api-key') == api_key:
            return view_func(request, *args, **kwargs)
        return JsonResponse([], safe=False, status=401)
    return wrapped_view


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


@api_key_required
@csrf_exempt
def tests_for_student(request: HttpRequest) -> JsonResponse:
    student_nr = request.POST.get('student-nr')

    if not student_nr:
        return JsonResponse([], safe=False, status=400)
    today = tz.localdate()

    try:
        appointment = EventAppointment.objects.get(date__exact=today, student_nr=student_nr)
    except EventAppointment.DoesNotExist:
        return JsonResponse('No appointment for student today', safe=False, status=404)

    return JsonResponse(appointment.extras.get('Toetsje'), safe=False)
