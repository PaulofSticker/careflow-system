from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Package
from .serializers import PackageSerializer


class PackageViewSet(ModelViewSet):
    queryset = Package.objects.all().order_by('-created_at')
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]