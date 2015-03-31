from rest_framework.viewsets import ViewSet
from django.http.response import JsonResponse

from authentication.config import FACEBOOK_PUBLIC, GITHUB_PUBLIC


class ConfigView(ViewSet):
    def list(self, request):
        return JsonResponse({
            'FACEBOOK_PUBLIC': FACEBOOK_PUBLIC,
            'GITHUB_PUBLIC': GITHUB_PUBLIC,
        })
