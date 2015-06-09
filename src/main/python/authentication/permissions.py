# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import calendar
import datetime
import pickle

from django.core import signing
from rest_framework.permissions import BasePermission, SAFE_METHODS

from hub.models import DocumentModel, FileGroupModel, FileModel, TransformationModel, UrlModel


"""
Contains the opendatahub specific permission profiles.
"""


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return hasattr(obj, 'owner') and obj.owner == request.user


class IsOwnerOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        safe = request.method in SAFE_METHODS
        user = self.user_from_token(request) or request.user
        if isinstance(obj, DocumentModel):
            return self._check_document_permission(safe, obj, user)
        elif isinstance(obj, FileGroupModel):
            return self._check_document_permission(safe, obj.document, user)
        elif isinstance(obj, (FileModel, UrlModel)):
            return self._check_document_permission(safe, obj.file_group.document, user)
        elif isinstance(obj, TransformationModel):
            return self._check_document_permission(safe, obj, user)

        return False

    def _check_document_permission(self, safe, doc, user):
        own = user and doc.owner == user
        return (not safe and own) or (safe and (own or not doc.private))

    def user_from_token(self, request):
        if 'token' not in request.query_params:
            return False
        token = signing.loads(request.query_params.get('token'))
        valid = token['valid_until'] > calendar.timegm(datetime.datetime.utcnow().timetuple())
        if not valid:
            return False
        return pickle.loads(token['owner'])
