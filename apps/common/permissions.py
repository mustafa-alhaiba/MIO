from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsLawyerOrAdmin(BasePermission):

    message = "Only lawyers and administrators may create or modify contracts."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ("LAWYER", "ADMIN")

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.role == "ADMIN":
            return True
        if obj.created_by_id == request.user.pk:
            return True
        return False


class IsAdminUser(BasePermission):

    message = "Only administrators may access this resource."

    def has_permission(self, request, view) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsContractPartyOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.role == "ADMIN":
            return True
        if obj.created_by_id == user.pk:
            return True
        return obj.parties.filter(pk=user.pk).exists()