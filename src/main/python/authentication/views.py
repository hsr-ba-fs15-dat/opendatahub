from calendar import timegm
import datetime

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from social.apps.django_app.utils import psa
from django.contrib.auth.models import User

from authentication.serializers import UserSerializer


class CurrentUserView(APIView):
    queryset = User.objects.all()

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@psa()
def auth_by_token(request, backend):
    """Decorator that creates/authenticates a user with an access_token"""
    token = request.data.get('access_token')
    user = request.user
    print("token")
    print(token)
    user = request.backend.do_auth(
        access_token=request.data.get('access_token')
    )
    if user:
        return user
    else:
        return None


class SocialView(APIView):
    """View to authenticate users through Facebook."""

    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        auth_token = request.data.get('access_token', None)
        backend = request.data.get('backend', None)
        if auth_token and backend:
            try:
                # Try to authenticate the user using python-social-auth
                user = auth_by_token(request, backend)
            except Exception, e:
                return Response({
                                'status': 'Bad request',
                                'message': 'Could not authenticate with the provided token.',
                                'error': e
                                }, status=status.HTTP_400_BAD_REQUEST)
            if user:
                if not user.is_active:
                    return Response({
                                    'status': 'Unauthorized',
                                    'message': 'The user account is disabled.'
                                    }, status=status.HTTP_401_UNAUTHORIZED)

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
            return Response({
                            'status': 'Bad request',
                            'message': 'Authentication could not be performed with received data.'
                            }, status=status.HTTP_400_BAD_REQUEST)
