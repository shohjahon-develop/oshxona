from django.db import transaction
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

        if table.is_occupied:
            if table.orders.filter(is_paid=False).exists():
                return Response({'error': 'Stolni bo‘shatish uchun barcha buyurtmalar to‘lanishi kerak.'},
                                status=status.HTTP_400_BAD_REQUEST)

        table.is_occupied = not table.is_occupied
        table.save()
        return Response({'status': 'updated', 'is_occupied': table.is_occupied}, status=status.HTTP_200_OK)


from rest_framework import viewsets
from .models import Order, Takeout, Delivery
from .serializers import OrderSerializer, TakeoutSerializer, DeliverySerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        items_data = request.data.pop('items', [])  # ✅ Itemsni ajratib olish

        with transaction.atomic():  # ✅ Transaction ishlatish
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()  # ✅ Buyurtmani saqlash

            # ✅ Itemsni bog‘lash
            for item in items_data:
                OrderItem.objects.create(order=order, menu_item_id=item["menu_item"], quantity=item["quantity"])

            order.calculate_total_price()  # ✅ Total narxni yangilash

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)




class TakeoutViewSet(viewsets.ModelViewSet):
    queryset = Takeout.objects.all()
    serializer_class = TakeoutSerializer

    def create(self, request, *args, **kwargs):
        items_data = request.data.pop('items', [])  # ✅ Itemsni ajratib olish

        with transaction.atomic():  # ✅ Transaction ishlatish
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            takeout = serializer.save()  # ✅ Buyurtmani saqlash

            # ✅ Itemsni bog‘lash
            for item in items_data:
                TakeoutItem.objects.create(order=takeout, menu_item_id=item["menu_item"], quantity=item["quantity"])

            takeout.calculate_total_price()  # ✅ Total narxni yangilash

        return Response(TakeoutSerializer(takeout).data, status=status.HTTP_201_CREATED)



class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    def create(self, request, *args, **kwargs):
        items_data = request.data.pop('items', [])  # ✅ Itemsni ajratib olish

        with transaction.atomic():  # ✅ Transaction ishlatish
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            delivery = serializer.save()  # ✅ Buyurtmani saqlash

            # ✅ Itemsni bog‘lash
            for item in items_data:
                DeliveryItem.objects.create(order=delivery, menu_item_id=item["menu_item"], quantity=item["quantity"])

            delivery.calculate_total_price()  # ✅ Total narxni yangilash

        return Response(DeliverySerializer(delivery).data, status=status.HTTP_201_CREATED)




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