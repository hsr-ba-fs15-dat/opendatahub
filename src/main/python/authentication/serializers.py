from rest_framework.serializers import ModelSerializer
from social.apps.django_app.default.models import UserSocialAuth

from authentication.models import UserProfile


class UserSocialAuthSerializer(ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ('provider', 'uid')


class UserSerializer(ModelSerializer):
    social_auth = UserSocialAuthSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'profile_photo', 'description', 'social_auth'
        )
