# roles/urls.py
from django.urls import path
# View nomini yangisiga o'zgartiramiz
from .views import RoleListCreateView, RoleDetailView, PermissionListCreateView

urlpatterns = [
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    # View nomini yangisiga o'zgartirdik
    path("permissions/", PermissionListCreateView.as_view(), name="permission-list-create"), # name ni ham o'zgartirish mumkin
]