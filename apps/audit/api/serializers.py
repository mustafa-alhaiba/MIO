from rest_framework import serializers

from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "action",
            "contract",
            "contract_title",
            "timestamp",
            "extra_data",
        ]
        read_only_fields = fields
