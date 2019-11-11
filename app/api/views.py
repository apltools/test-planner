import datetime as dt
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.models import model_to_dict
from django.http import HttpRequest, JsonResponse
from django.template.defaultfilters import date as _date

from planner.models import Appointment, Course, Test, TestMoment


def staff_member_required_json(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return JsonResponse([], safe=False, status=401)

    return wrapped_view


class AppointmentsEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Appointment):
            obj_dict = model_to_dict(obj, fields=['student_name', 'tests', 'id'])
            obj_dict['course'] = obj.course.short_name
            return obj_dict

        elif isinstance(obj, Test):
            return obj.name

        elif isinstance(obj, Course):
            return obj.name

        elif isinstance(obj, dt.date):
            return _date(obj, "l j F").capitalize()

        elif isinstance(obj, models.Model):
            return model_to_dict(obj)

        return super().default(obj)


@staff_member_required_json
def appointments(request: HttpRequest, test_moment_id) -> JsonResponse:
    test_moment = TestMoment.objects.get(id__exact=test_moment_id)
    apps = test_moment.appointments_for_moment
    return JsonResponse({'test_moment': test_moment, 'appointments': apps}, encoder=AppointmentsEncoder, safe=False)


@staff_member_required_json
def cancel_appointment(request: HttpRequest) -> JsonResponse:
    try:
        app_id = int(request.POST.get('app_id'))
        Appointment.objects.get(id__exact=app_id).delete()
    except:
        return JsonResponse(False, safe=False)
    return JsonResponse(True, safe=False)
