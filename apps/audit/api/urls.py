from rest_framework.routers import DefaultRouter

from apps.audit.api.views import AuditLogViewSet

router = DefaultRouter()
router.register(r"audit", AuditLogViewSet, basename="audit")

urlpatterns = router.urls
