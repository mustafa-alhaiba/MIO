from apps.common.context import set_current_user


class CurrentUserMiddleware:
    """
    Clears the thread-local user at the end of every request.
    The actual user is set by AuditJWTAuthentication after token validation,
    because JWT auth happens inside DRF view dispatch — not in middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        finally:
            set_current_user(None)
