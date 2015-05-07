# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission, SAFE_METHODS

from hub.models import DocumentModel, FileGroupModel, FileModel, TransformationModel, UrlModel


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return hasattr(obj, 'owner') and obj.owner == request.user


class IsOwnerOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        safe = request.method in SAFE_METHODS

        if isinstance(obj, DocumentModel):
            return self._check_document_permission(safe, obj, request.user)
        elif isinstance(obj, FileGroupModel):
            return self._check_document_permission(safe, obj.document, request.user)
        elif isinstance(obj, (FileModel, UrlModel)):
            return self._check_document_permission(safe, obj.file_group.document, request.user)
        elif isinstance(obj, TransformationModel):
            return self._check_document_permission(safe, obj, request.user)

        return False

    def _check_document_permission(self, safe, doc, user):
        own = user and doc.owner == user
        return (not safe and own) or (safe and (own or not doc.private))
