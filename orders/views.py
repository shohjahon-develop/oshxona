from rest_framework import viewsets
from .models import Order, Table, Takeout, Delivery
from .serializers import OrderSerializer, TableSerializer, TakeoutSerializer, DeliverySerializer
from rest_framework.permissions import IsAuthenticated

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class TakeoutViewSet(viewsets.ModelViewSet):
    queryset = Takeout.objects.all()
    serializer_class = TakeoutSerializer
    permission_classes = [IsAuthenticated]

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]