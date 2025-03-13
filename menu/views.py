

from rest_framework import viewsets
from .models import MenuItem
from .serializers import MenuItemSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    parser_classes = (MultiPartParser, FormParser)

