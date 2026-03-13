from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.contracts import models
from apps.common import file_validator

User = get_user_model()


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role")
        read_only_fields = fields


class ContractSerializer(serializers.ModelSerializer):
    parties = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    created_by = serializers.StringRelatedField(read_only=True)
    is_expired  = serializers.BooleanField(read_only=True)

    arabic_title = serializers.CharField(
        required=False,
        allow_blank=True,
        style={"direction": "rtl", "text_align": "right"},
        help_text="Arabic contract title — rendered right-to-left.",
    )
    
    class Meta:
        model  = models.Contract
        fields = [
            "id",
            "title",
            "arabic_title",
            "description",
            "status",
            "parties",
            "created_by",
            "created_at",
            "updated_at",
            "deadline",
            "document",
            "is_expired",
            "deleted_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "deleted_at"]
        extra_kwargs = {
            "document": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["parties"] = PartySerializer(
            instance.parties.all(), many=True, context=self.context
        ).data
        return data

    def validate_status(self, value: str) -> str:
        
        request = self.context.get("request")
        if value in (models.Contract.Status.EXPIRED, models.Contract.Status.ARCHIVED):
            if request and request.user.role != "ADMIN":
                raise serializers.ValidationError(
                    "Only an ADMIN can set status to EXPIRED or ARCHIVED."
                )
        return value


class ContractDocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField()

    def validate_document(self, file_obj):
        file_validator.validate_contract_document(file_obj)
        return file_obj