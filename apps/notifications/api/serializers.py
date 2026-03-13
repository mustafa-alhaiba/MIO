from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    contract_title = serializers.CharField(source="contract.title", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "contract", "contract_title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "contract", "contract_title", "message", "created_at"]
