from rest_framework.relations import PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer, StringRelatedField
from social.apps.django_app.default.models import DjangoStorage, UserSocialAuth
from authentication.models import UserProfile


class UserSerializer(ModelSerializer):
    # social_data = PrimaryKeyRelatedField()

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_photo')


class UserAuthSerializer(ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ('extra_data', 'provider')