from functools import wraps

from django.http import JsonResponse


def staff_member_required_json(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return JsonResponse([], safe=False, status=401)

    return wrapped_view
