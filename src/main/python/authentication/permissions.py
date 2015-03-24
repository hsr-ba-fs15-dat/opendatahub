from rest_framework.permissions import BasePermission, SAFE_METHODS

from hub.models import DocumentModel, FileGroupModel, FileModel

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.owner == request.user

class IsOwnerOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if isinstance(obj, DocumentModel):
                return self._check_document_permission(obj, request.user)
            elif isinstance(obj, FileGroupModel):
                return self._check_document_permission(obj.document, request.user)
            elif isinstance(obj, FileModel):
                return self._check_document_permission(obj.file_group.document, request.user)
            else:
                return False

        return request.user is not None

    def _check_document_permission(self, doc, user):
        return not doc.private or (user and doc.owner == user)