from calendar import timegm
import datetime
from urlparse import parse_qsl

import requests
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from social.apps.django_app.utils import psa
from django.contrib.auth.models import User

from authentication import config
from authentication.serializers import UserSerializer


class PublicKeysView(APIView):
    def get(self):
        return {'facebook': config.FACEBOOK_PUBLIC,
                'github': config.GITHUB_PUBLIC
        }


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()

    def get(self, request):
        print(request.data)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@psa()
def auth_by_token(request, backend, auth_token):
    """Decorator that creates/authenticates a user with an access_token"""

    user = request.backend.do_auth(
        access_token=auth_token
    )
    if user:
        return user
    else:
        return None


def get_access_token(request, backend):
    if backend == "facebook":
        return request.data.get(u'access_token', None)
    if backend == "github":
        access_token_url = 'https://github.com/login/oauth/access_token'

        params = {
            'client_id': request.data.get('clientId'),
            'redirect_uri': request.data.get('redirectUri'),
            'client_secret': config.GITHUB_SECRET,
            'code': request.data.get('code')
        }

        # Step 1. Exchange authorization code for access token.
        r = requests.get(access_token_url, params=params)
        access_token = dict(parse_qsl(r.text))['access_token']
        return access_token


class SocialView(APIView):
    """View to authenticate users through Facebook."""

    permission_classes = (AllowAny,)

    def post(self, request, format=None):

        backend = request.data.get(u'backend', None)

        auth_token = get_access_token(request, backend)

        if auth_token and backend:
            try:
                # Try to authenticate the user using python-social-auth
                user = auth_by_token(request, backend, auth_token)

            except Exception:
                return Response({'status': 'Bad request',
                                 'message': 'Could not authenticate with the provided token.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user:
                if not user.is_active:
                    return Response({'status': 'Unauthorized',
                                     'message': 'The user account is disabled.'}, status=status.HTTP_401_UNAUTHORIZED)

                # This is the part that differs from the normal python-social-auth implementation.
                # Return the JWT instead.

                # Get the JWT payload for the user.
                payload = jwt_payload_handler(user)

                # Include original issued at time for a brand new token,
                # to allow token refresh
                if api_settings.JWT_ALLOW_REFRESH:
                    payload['orig_iat'] = timegm(
                        datetime.datetime.utcnow().utctimetuple()
                    )

                # Create the response object with the JWT payload.
                response_data = {
                    'token': jwt_encode_handler(payload)
                }

                return Response(response_data)
        else:
            return Response({'status': 'Bad request',
                             'message': 'Authentication could not be performed with received data.'},
                            status=status.HTTP_400_BAD_REQUEST)
