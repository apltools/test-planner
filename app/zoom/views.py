from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from planner.models import User
from .decorators import zoom_token_required
from .models import OAuth2Token
from .zoom_api_handler import zoom


@login_required
def index(request: HttpRequest) -> HttpResponse:
    print(request.build_absolute_uri())
    user: User = request.user

    if user.has_zoom_token():
        resp = zoom.get('users/me', request=request)
        me = resp.json()
    else:
        me = False

    return JsonResponse(me, safe=False)


@login_required
def unlink(request: HttpRequest) -> HttpResponse:
    try:
        token = OAuth2Token.objects.get(name='zoom', user=request.user)
        token.delete()
        return HttpResponse('True')
    except OAuth2Token.DoesNotExist:
        return HttpResponse('No Account linked')


@login_required
def login(request: HttpRequest) -> HttpResponse:
    redirect_uri = request.build_absolute_uri(reverse('zoom:authorize'))

    if next_link := request.GET.get('next'):
        redirect_uri += f'?next={next_link}'

    return zoom.authorize_redirect(request, redirect_uri)


@login_required
def authorize(request: HttpRequest) -> HttpResponse:
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

    return redirect('zoom:index')


@login_required
@zoom_token_required
def meetings(request: HttpRequest) -> HttpResponse:
    meeting_type = request.GET.get('type') if 'type' in request.GET else 'schduled'

    querystring = {"page_number": "1", "page_size": "30", "type": meeting_type}
    resp = zoom.get('users/me/meetings', request=request, params=querystring)
    meetings = resp.json()

    return JsonResponse(meetings, safe=False)
