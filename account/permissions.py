from rest_framework.permissions import BasePermission


class IsPhoneVerified(BasePermission):
    message = 'your phone number is not verified'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_phone_verified
