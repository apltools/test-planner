from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from zoom.models import OAuth2Token


def zoom_token_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except OAuth2Token.DoesNotExist:
            return redirect(f'{reverse("zoom:login")}?next={request.path}')
        # except

    return wrapped_view