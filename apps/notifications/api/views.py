from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.notifications.models import Notification
from apps.notifications.api.serializers import NotificationSerializer
from apps.common import paginations

class NotificationViewSet(ModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]
    pagination_class = paginations.StandardResultsSetPagination
    
    def get_queryset(self):
        return (
            Notification.objects.filter(recipient=self.request.user, is_read=False)
            .select_related("contract")
        )

    @action(detail=True, methods=["patch"], url_path="read")
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data, status=status.HTTP_200_OK)
