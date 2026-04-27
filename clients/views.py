from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all().order_by('full_name')
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]