import time
from functools import wraps


from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import models
from django.views.decorators.http import require_POST

from planner.models import Course, TestMoment, Appointment, Test


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
            return model_to_dict(obj, exclude=['cancel_secret'])
        if isinstance(obj, Test):
            return obj.name
        if isinstance(obj, Course):
            return obj.name
        elif isinstance(obj, models.Model):
            return model_to_dict(obj)
        return super().default(obj)


# @require_POST
@staff_member_required_json
def appointments(request: HttpRequest, test_moment_id) -> JsonResponse:
    test_moment = TestMoment.objects.get(id__exact=test_moment_id)
    apps = test_moment.appointments_for_moment
    return JsonResponse({'test_moment': test_moment, 'appointments': apps}, encoder=AppointmentsEncoder, safe=False)
