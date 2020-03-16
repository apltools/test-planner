from pprint import pprint

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from dash.decorators import teaching_assistant_required
from .decorators import zoom_token_required
from .models import OAuth2Token
from .zoom_api_handler import zoom


# Create your views here.


@teaching_assistant_required
def login(request):
    # build a full authorize callback uri
    redirect_uri = request.build_absolute_uri(reverse('zoom:authorize'))

    if next := request.GET.get('next'):
        redirect_uri += f'?next={next}'

    return zoom.authorize_redirect(request, redirect_uri)


@teaching_assistant_required
def authorize(request):
    if not OAuth2Token.objects.filter(name='zoom', user=request.user):
        token = zoom.authorize_access_token(request, grand_type='authorization_code')

        OAuth2Token(
            name='zoom',
            token_type=token['token_type'],
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            expires_at=token['expires_at'],
            user=request.user
        ).save()

    if next := request.GET.get('next'):
        return redirect(next)

    return HttpResponse('true')


@teaching_assistant_required
@zoom_token_required
def meetings(request):
    querystring = {"page_number": "1", "page_size": "30", "type": "scheduled"}
    resp = zoom.get('users/me/meetings', request=request, params=querystring)
    meetings = resp.json()
    pprint(meetings)
    return JsonResponse(meetings, safe=False)
