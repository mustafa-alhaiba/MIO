from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.common.context import set_current_user


class AuditJWTAuthentication(JWTAuthentication):
    """
    Extends JWTAuthentication to populate the thread-local current user
    immediately after token validation, so Django signals fired during
    the request lifecycle can read the authenticated user.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, _ = result
            set_current_user(user)
        return result
