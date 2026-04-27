from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(ModelViewSet):
    queryset = Session.objects.all().order_by('-scheduled_date', '-scheduled_time')
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
