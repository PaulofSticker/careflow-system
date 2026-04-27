from rest_framework.routers import DefaultRouter
from .views import InstallmentViewSet

router = DefaultRouter()
router.register(r'', InstallmentViewSet, basename='installment')

urlpatterns = router.urls