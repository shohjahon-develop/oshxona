# roles/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser # Ruxsatlarni import qilish
from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer

class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # Rollarni ham admin boshqarsin

# --- O'ZGARTIRILGAN VIEW ---
class PermissionListCreateView(generics.ListCreateAPIView): # Nomini va voris olishni o'zgartirdik
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # Faqat adminlar permission qo'sha olsin
# --- -------------- ---

class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # Detallarni ham admin boshqarsin