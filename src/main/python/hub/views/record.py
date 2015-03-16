from rest_framework import viewsets

from hub.models import RecordModel
from hub.serializers import RecordSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = RecordModel.objects.all()
    serializer_class = RecordSerializer

    paginate_by = 50
