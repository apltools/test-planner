import datetime as dt

from authlib.integrations.django_client import OAuth, DjangoRemoteApp

from planner.models import User, EventAppointment
from .models import OAuth2Token, ZoomMeeting

from http import HTTPStatus


def fetch_token(name, request):
    return OAuth2Token.objects.get(
        name=name,
        user=request.user
    ).to_token()


def get_token_for_user(user: User, name='zoom'):
    return OAuth2Token.objects.get(
        name=name,
        user=user,
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


def create_meeting(app: EventAppointment) -> ZoomMeeting:
    token = get_token_for_user(app.host)
    request_body = {
        "topic": f'{app.name}: {app.event.event_type.name}',
        "type": 2,
        "start_time": dt.datetime.combine(app.date, app.start_time).isoformat(),
        "duration": app.duration,
        "timezone": "Europe/Amsterdam",
        "settings": {
            "host_video": False,
            "participant_video": False,
            "join_before_host": True,
            "mute_upon_entry": False,
            "audio": "voip",
        }
    }

    resp = zoom.post('users/me/meetings', json=request_body, token=token)
    meeting = resp.json()
    print(meeting)
    zoom_meeting = ZoomMeeting(
        meeting_id=meeting['id'],
        meeting_url=meeting['join_url'],
    )

    zoom_meeting.save()

    return zoom_meeting


def delete_meeting(app: EventAppointment):
    token = get_token_for_user(app.host)
    resp = zoom.delete(f'meetings/{app.zoom_meeting.meeting_id}',
                       params={"schedule_for_reminder": "false"},
                       token=token)

    if resp.status_code == HTTPStatus.NO_CONTENT:
        return True

    status = HTTPStatus(resp.status_code)
    print(f'{status.value} {status.phrase}: {status.description}')

    return False
