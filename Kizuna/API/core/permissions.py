from django.core.exceptions import ValidationError
from rest_framework import permissions
from API.models import TokenImport


class SuccessToken(permissions.BasePermission):
    """Разрешение проверяющее оплачен ли доступ у пользователя"""

    def has_permission(self, request, view):
        try:
            token = request.GET.get("token")
            return TokenImport.objects.filter(token=token).exists()
        except ValidationError:
            return False

