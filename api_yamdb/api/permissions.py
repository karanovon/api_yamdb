from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Проверка прав доступа для объектов: разрешает доступ только автору,
    администратору, модераторау на безопасные методы.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )
