from datetime import datetime

from authlib.integrations.django_client import OAuth, DjangoRemoteApp
from django.http import HttpRequest

from .models import OAuth2Token


def fetch_token(name, request):
    return OAuth2Token.objects.get(
        name=name,
        user=request.user
    ).to_token()


def update_token(name, token, refresh_token=None, access_token=None):
    if refresh_token:
        item = OAuth2Token.objects.get(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.objects.get(name=name, access_token=access_token)
    else:
        return

    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']

    item.save()


oauth = OAuth(fetch_token=fetch_token, update_token=update_token)

oauth.register(
    name='zoom',
    client_id='2i73OLm1R2CCBEN6Spyt4g',
    client_secret='fFLXguSGF8DWZzbDR3956kT7f3fh455J',

    access_token_url='https://zoom.us/oauth/token',
    access_token_params=None,

    authorize_url='https://zoom.us/oauth/authorize',
    authorize_params=None,

    api_base_url='https://api.zoom.us/v2/',
    client_kwargs={
        'token_endpoint_auth_method': 'client_secret_basic',
        'token_placement': 'header',
    },
)

zoom: DjangoRemoteApp = oauth.zoom


def create_meeting(request: HttpRequest):
    request_body = {
        "topic": "test",
        "type": 2,
        "start_time": datetime(2020, 3, 20, 10, 00).isoformat(),
        "duration": 10,
        "timezone": "Europe/Amsterdam",
        "settings": {
            "host_video": False,
            "participant_video": False,
            "join_before_host": True,
            "mute_upon_entry": False,
            "audio": "voip",
        }
    }

    return zoom.post('users/me/meetings', json=request_body, request=request)
