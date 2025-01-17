# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from social.apps.django_app.default.models import UserSocialAuth

from authentication.models import UserProfile


class UserSocialAuthSerializer(ModelSerializer):
    """
    Gets the login name from different social media profiles.
    """
    login = serializers.SerializerMethodField('get_the_login')

    class Meta(object):
        model = UserSocialAuth
        fields = ('provider', 'uid', 'login')

    def get_the_login(self, obj):
        try:
            login = obj.extra_data['login']
        except KeyError:
            login = obj.uid
        return login


class UserSerializer(ModelSerializer):
    """
    Contains the full user profile.
    """
    social_auth = UserSocialAuthSerializer(
        many=True,
        read_only=True,
    )

    class Meta(object):
        model = UserProfile
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'profile_photo', 'description', 'social_auth'
        )


class UserDisplaySerializer(ModelSerializer):
    """
    Contains the limited user profile. Viewed by other users.
    """
    class Meta(object):
        model = UserProfile
        fields = (
            'id', 'username', 'first_name', 'last_name'
        )
