from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .serializers import *

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


    @action(detail=True, methods=['post'])
    def toggle_occupancy(self, request, pk=None):
        table = self.get_object()
        table.is_occupied = not table.is_occupied  # Band yoki bo‘sh qilish
        table.save()
        return Response({'status': 'updated', 'is_occupied': table.is_occupied}, status=status.HTTP_200_OK)


from rest_framework import viewsets
from .models import Order, Takeout, Delivery
from .serializers import OrderSerializer, TakeoutSerializer, DeliverySerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        order.calculate_total_price()  # ✅ Buyurtma yaratishda umumiy narx hisoblanadi

    def perform_update(self, serializer):
        order = serializer.save()
        order.calculate_total_price()  # ✅ Buyurtma yangilansa umumiy narx qayta hisoblanadi

class TakeoutViewSet(viewsets.ModelViewSet):
    queryset = Takeout.objects.all()
    serializer_class = TakeoutSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        order.calculate_total_price()

    def perform_update(self, serializer):
        order = serializer.save()
        order.calculate_total_price()

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    def perform_create(self, serializer):
        order = serializer.save()
        order.calculate_total_price()

    def perform_update(self, serializer):
        order = serializer.save()
        order.calculate_total_price()



class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]


class TakeoutItemViewSet(viewsets.ModelViewSet):
    queryset = TakeoutItem.objects.all()
    serializer_class = TakeoutItemSerializer
    permission_classes = [IsAuthenticated]


class DeliveryItemViewSet(viewsets.ModelViewSet):
    queryset = DeliveryItem.objects.all()
    serializer_class = DeliveryItemSerializer
    permission_classes = [IsAuthenticated]