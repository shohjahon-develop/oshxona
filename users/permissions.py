# users/permissions.py

from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Faqat 'admin' rolidagi foydalanuvchilarga ruxsat beradi.
    """
    message = 'Bu amalni bajarish uchun Admin huquqi talab qilinadi.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsDeliveryRole(permissions.BasePermission):
    """
    Faqat 'delivery' rolidagi foydalanuvchilarga ruxsat beradi.
    """
    message = 'Bu amalni bajarish uchun Yetkazib beruvchi huquqi talab qilinadi.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'delivery')

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Har qanday autentifikatsiyadan o'tgan foydalanuvchiga o'qishga ruxsat beradi,
    lekin yozish uchun faqat adminlarga ruxsat beradi.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # GET, HEAD, OPTIONS so'rovlari xavfsiz hisoblanadi (o'qish)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Yozish (POST, PUT, PATCH, DELETE) uchun faqat adminlarga ruxsat
        return request.user.role == 'admin'

# Kerak bo'lsa boshqa rollar uchun ham shunga o'xshash permission classlar yaratishingiz mumkin
# Masalan: IsChefRole, IsCashierRole, IsWaiterRole


class IsAdminOrDeliveryRole(permissions.BasePermission):
    message = 'Bu amalni bajarish uchun Admin yoki Yetkazib beruvchi huquqi talab qilinadi.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'admin' or request.user.role == 'delivery')
        )