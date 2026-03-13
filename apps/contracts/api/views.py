from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.common import permissions
from apps.contracts.api import serializers
from apps.contracts import services
from apps.common import paginations


class ContractViewSet(ModelViewSet):

    serializer_class   = serializers.ContractSerializer
    permission_classes = [IsAuthenticated, permissions.IsLawyerOrAdmin]
    pagination_class  = paginations.StandardResultsSetPagination
    
    # ------------------------------------------------------------------
    # Queryset & permissions
    # ------------------------------------------------------------------

    def get_queryset(self):
        qs = services.ContractService.get_queryset_for_user(self.request.user)
        return services.ContractService.apply_filters(qs, self.request.query_params)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), permissions.IsContractPartyOrAdmin()]
        return super().get_permissions()

    # ------------------------------------------------------------------
    # Overrides — delegate to service, never put logic here
    # ------------------------------------------------------------------

    def perform_create(self, serializer):
        contract = services.ContractService.create_contract(
            validated_data=serializer.validated_data.copy(),
            created_by=self.request.user,
        )
        serializer.instance = contract

    def perform_update(self, serializer):
        services.ContractService.update_contract(
            contract=serializer.instance,
            validated_data=serializer.validated_data.copy(),
        )

    def perform_destroy(self, instance):
        services.ContractService.soft_delete_contract(instance)

    # ------------------------------------------------------------------
    # Custom action: POST /api/contracts/{id}/upload/
    # ------------------------------------------------------------------

    @action(
        detail=True,
        methods=["post"],
        url_path="upload",
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[IsAuthenticated, permissions.IsLawyerOrAdmin],
    )
    def upload(self, request, *args, **kwargs):
        contract = self.get_object()

        upload_serializer = serializers.ContractDocumentUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)

        contract = services.ContractService.attach_document(
            contract=contract,
            file_obj=upload_serializer.validated_data["document"],
        )

        return Response(
            serializers.ContractSerializer(contract, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )