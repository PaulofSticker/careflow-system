from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Installment
from .serializers import InstallmentSerializer


class InstallmentViewSet(ModelViewSet):
    queryset = Installment.objects.all().order_by('-created_at')
    serializer_class = InstallmentSerializer
    permission_classes = [IsAuthenticated]
