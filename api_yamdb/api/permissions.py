from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Проверка прав администратора."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    request.user.is_admin or request.user.is_superuser
                )
            )
        )


class IsStaffOrAuthorOrReadOnly(permissions.BasePermission):
    """Проверка прав для отзывов и комментариев."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_admin
                or request.user.is_moderator
                or request.user == obj.author
                )


class IsAdminOrSuperUser(permissions.BasePermission):
    """Разрешение для админа или суперпользователя."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение для авторизованного или неавторизованного пользователя."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
