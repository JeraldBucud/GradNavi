from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allow access only to authenticated GradNavi administrators.
    """

    message = "Administrator access is required."

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and user.role == user.Role.ADMIN
        )