from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.audit.api.serializers import AuditLogSerializer
from apps.audit.models import AuditLog
from apps.common.paginations import StandardResultsSetPagination
from apps.common.permissions import IsAdminUser


class AuditLogViewSet(ReadOnlyModelViewSet):

    serializer_class   = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class   = StandardResultsSetPagination

    def get_queryset(self):
        qs = AuditLog.objects.select_related("user", "contract")

        contract_id = self.request.query_params.get("contract_id")
        user_id     = self.request.query_params.get("user_id")
        action      = self.request.query_params.get("action")

        if contract_id:
            qs = qs.filter(contract_id=contract_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if action:
            qs = qs.filter(action=action.upper())

        return qs
