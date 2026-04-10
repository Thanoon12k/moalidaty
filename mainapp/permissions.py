from rest_framework.permissions import BasePermission


class IsGeneratorAuthenticated(BasePermission):
    """Either an account manager or a worker of any generator.
    Used for read/write operations that both roles may perform (e.g. receipts)."""
    message = 'يجب تسجيل الدخول للوصول إلى هذه البيانات'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.get('generator_id')
            and request.user.get('type') in ('account', 'worker')
        )


class IsAccountOnly(BasePermission):
    """Only the generator account manager (not workers) may access.
    Used for sensitive operations: budgets, workers management, account settings."""
    message = 'هذه العملية متاحة لمدير المولدة فقط'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.get('type') == 'account'
        )
