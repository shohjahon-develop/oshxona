## orders/views.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.permissions import IsAdminOrDeliveryRole
# Endi User kerak emas (agar boshqa joyda ishlatilmasa)
# from .models import Table, Order, Takeout, Delivery, User
from .models import Table, Order, Takeout, Delivery
from .serializers import (
    TableSerializer, OrderSerializer, TakeoutSerializer, DeliverySerializer,
    OrderStatusUpdateSerializer, TakeoutStatusUpdateSerializer, DeliveryStatusUpdateSerializer,
    # DeliveryAssignSerializer, # Kerak emas
)
# users.permissions kerak emas endi
# from users.permissions import IsAdminRole, IsDeliveryRole

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated] # Yoki IsAdminUser


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer # Soddalashtirilgan serializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method='patch',
        request_body=OrderStatusUpdateSerializer,
        responses={200: OrderSerializer, 400: 'Validation Error', 403: 'Permission Denied'}
    )
    @action(detail=True, methods=['patch'], url_path='update-status', permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            order.status = serializer.validated_data['status']
            print(f"--- Before save - Order ID: {order.id}, Status: {order.status}, Price: {order.total_price} ---")
            order.save()
            # Saqlangandan keyin bazadan qayta o'qib ko'rish yaxshiroq
            order.refresh_from_db()
            print(f"--- After save - Order ID: {order.id}, Status: {order.status}, Price: {order.total_price} ---")
            response_serializer = self.get_serializer(order)
            return Response(response_serializer.data, status=status.HTTP_200_OK)


class TakeoutViewSet(viewsets.ModelViewSet):
    queryset = Takeout.objects.all().order_by('-created_at')
    serializer_class = TakeoutSerializer # Soddalashtirilgan serializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method='patch',
        request_body=TakeoutStatusUpdateSerializer,
        responses={200: TakeoutSerializer, 400: 'Validation Error', 403: 'Permission Denied'}
    )
    @action(detail=True, methods=['patch'], url_path='update-status', permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        takeout = self.get_object()
        serializer = TakeoutStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            takeout.status = serializer.validated_data['status']
            takeout.save()
            response_serializer = self.get_serializer(takeout)
            return Response(response_serializer.data, status=status.HTTP_200_OK) # 200 OK
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer # Soddalashtirilgan serializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method='patch',
        request_body=DeliveryStatusUpdateSerializer,
        responses={200: DeliverySerializer, 400: 'Validation Error', 403: 'Permission Denied'}
    )
    @action(detail=True, methods=['patch'], url_path='update-status', permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        delivery = self.get_object()
        # Haydovchi tekshiruvi olib tashlandi
        serializer = DeliveryStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            delivery.status = serializer.validated_data['status']
            delivery.save()
            response_serializer = self.get_serializer(delivery)
            return Response(response_serializer.data, status=status.HTTP_200_OK) # 200 OK
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- assign-driver action olib tashlandi ---
    # @action(detail=True, methods=['patch'], url_path='assign-driver', permission_classes=[IsAdminUser])
    # def assign_driver(self, request, pk=None):
    #     ...

# --- MyDeliveriesView olib tashlandi ---
# class MyDeliveriesView(APIView):
#     ...

# ServedOrdersView o'zgarishsiz qoladi, lekin soddalashtirilgan serializerlarni ishlatadi
class ServedOrdersView(APIView):
    permission_classes = [IsAuthenticated] # Yoki Adminlar uchun

    def get(self, request):
        orders = Order.objects.filter(status='served').order_by('-created_at')
        takeouts = Takeout.objects.filter(status='served').order_by('-created_at')
        deliveries = Delivery.objects.filter(status='served').order_by('-created_at')

        # Soddalashtirilgan serializerlar ishlatiladi
        orders_serializer = OrderSerializer(orders, many=True)
        takeouts_serializer = TakeoutSerializer(takeouts, many=True)
        deliveries_serializer = DeliverySerializer(deliveries, many=True)

        data = {
            'orders': orders_serializer.data,
            'takeouts': takeouts_serializer.data,
            'deliveries': deliveries_serializer.data,
        }
        return Response(data)









# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.exceptions import ValidationError
# from rest_framework.views import APIView
#
# from .models import Table, Order, Takeout, Delivery
# from .serializers import TableSerializer, OrderSerializer, TakeoutSerializer, DeliverySerializer
#
#
# class TableViewSet(viewsets.ModelViewSet):
#     queryset = Table.objects.all()
#     serializer_class = TableSerializer
#     permission_classes = [IsAuthenticated]
#
#
# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#
#     @action(detail=True, methods=['post'], url_path='update-status')
#     def update_status(self, request, pk=None):
#         order = self.get_object()
#         serializer = OrderSerializer(order, data={'status': request.data.get('status')}, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class TakeoutViewSet(viewsets.ModelViewSet):
#     queryset = Takeout.objects.all()
#     serializer_class = TakeoutSerializer
#     permission_classes = [IsAuthenticated]
#
#     @action(detail=True, methods=['post'], url_path='update-status')
#     def update_status(self, request, pk=None):
#         takeout = self.get_object()
#         serializer = TakeoutSerializer(takeout, data={'status': request.data.get('status')}, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_201_CREATED)
#
#
# class DeliveryViewSet(viewsets.ModelViewSet):
#     queryset = Delivery.objects.all()
#     serializer_class = DeliverySerializer
#     permission_classes = [IsAuthenticated]
#
#     @action(detail=True, methods=['post'], url_path='update-status')
#     def update_status(self, request, pk=None):
#         delivery = self.get_object()
#         serializer = DeliverySerializer(delivery, data={'status': request.data.get('status')}, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_201_CREATED)
#
#
#
#
#
# class ServedOrdersView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         orders = Order.objects.filter(status='served')
#         takeouts = Takeout.objects.filter(status='served')
#         deliveries = Delivery.objects.filter(status='served')
#
#         orders_serializer = OrderSerializer(orders, many=True)
#         takeouts_serializer = TakeoutSerializer(takeouts, many=True)
#         deliveries_serializer = DeliverySerializer(deliveries, many=True)
#
#         data = {
#             'orders': orders_serializer.data,
#             'takeouts': takeouts_serializer.data,
#             'deliveries': deliveries_serializer.data,
#         }
#
#         return Response(data)