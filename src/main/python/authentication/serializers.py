# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from social.apps.django_app.default.models import UserSocialAuth

from authentication.models import UserProfile


class UserSocialAuthSerializer(ModelSerializer):
    login = serializers.SerializerMethodField('get_the_login')

    class Meta:
        model = UserSocialAuth
        fields = ('provider', 'uid', 'login')

    def get_the_login(self, obj):
        try:
            login = obj.extra_data['login']
        except KeyError:
            login = obj.uid
        return login


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
