# orders/views.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Table, Order, Takeout, Delivery, User
from .serializers import (
    TableSerializer, OrderSerializer, TakeoutSerializer, DeliverySerializer,
    OrderStatusUpdateSerializer, TakeoutStatusUpdateSerializer, DeliveryStatusUpdateSerializer,
    DeliveryAssignSerializer, # Import qilindi
)
from users.permissions import IsAdminRole, IsDeliveryRole # Kerakli permissions

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated] # Yoki IsAdminUser


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at') # Oxirgilari birinchi
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] # Umumiy dostup

    # Statusni alohida action bilan yangilash
    @swagger_auto_schema(
        method='patch',
        request_body=OrderStatusUpdateSerializer,
        responses={200: OrderSerializer, 400: 'Validation Error', 403: 'Permission Denied'}
    )
    @action(detail=True, methods=['patch'], url_path='update-status', permission_classes=[IsAuthenticated]) # Kimlar o'zgartira olishini cheklash mumkin
    def update_status(self, request, pk=None):
        order = self.get_object()
        # Qo'shimcha tekshiruvlar: Masalan, faqat ma'lum rollar statusni o'zgartira olsin
        # if not (request.user.role in ['admin', 'waiter', 'chef', 'cashier']):
        #     raise PermissionDenied("Sizda bu amalni bajarish uchun huquq yo'q.")

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            # Status o'zgarish logikasi (masalan, 'served' dan 'pending' ga o'tkazib bo'lmasin)
            # if order.status == 'served' and new_status != 'served':
            #     return Response({'error': 'Yakunlangan buyurtma statusini o'zgartirib bo\'lmaydi.'}, status=status.HTTP_400_BAD_REQUEST)

            order.status = new_status
            order.save()
            # Yangilangan orderni to'liq serializer bilan qaytarish
            response_serializer = self.get_serializer(order)
            return Response(response_serializer.data, status=status.HTTP_200_OK) # 200 OK qaytaramiz
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TakeoutViewSet(viewsets.ModelViewSet):
    queryset = Takeout.objects.all().order_by('-created_at')
    serializer_class = TakeoutSerializer
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
    queryset = Delivery.objects.all().order_by('-created_at')
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated] # Umumiy dostup

    @swagger_auto_schema(
        method='patch',
        request_body=DeliveryStatusUpdateSerializer,
        responses={200: DeliverySerializer, 400: 'Validation Error', 403: 'Permission Denied'}
    )
    @action(detail=True, methods=['patch'], url_path='update-status', permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        delivery = self.get_object()
        # Faqat tayinlangan delivery driver yoki admin statusni o'zgartira olsin
        if not (request.user.role == 'admin' or delivery.assigned_to == request.user):
             raise PermissionDenied("Siz bu buyurtma statusini o'zgartira olmaysiz.")

        serializer = DeliveryStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            # Qo'shimcha logikalar, masalan, driver faqat 'preparing' -> 'ready' yoki 'ready' -> 'served' qila olsin
            delivery.status = new_status
            delivery.save()
            response_serializer = self.get_serializer(delivery)
            return Response(response_serializer.data, status=status.HTTP_200_OK) # 200 OK
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- YANGI ACTION: Yetkazib beruvchini tayinlash (Faqat Admin uchun) ---
    @swagger_auto_schema(
        method='patch',
        request_body=DeliveryAssignSerializer,
        responses={200: DeliverySerializer, 400: 'Validation Error', 403: 'Permission Denied'}
    )
    @action(detail=True, methods=['patch'], url_path='assign-driver', permission_classes=[IsAdminUser]) # Yoki IsAdminRole
    def assign_driver(self, request, pk=None):
        delivery = self.get_object()
        serializer = DeliveryAssignSerializer(data=request.data)
        if serializer.is_valid():
            delivery.assigned_to = serializer.validated_data['assigned_to']
            delivery.save()
            response_serializer = self.get_serializer(delivery)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- YANGI VIEW: Yetkazib beruvchi uchun o'zining buyurtmalari ---
class MyDeliveriesView(APIView):
    """
    Autentifikatsiyadan o'tgan va 'delivery' rolida bo'lgan foydalanuvchi uchun
    unga tayinlangan buyurtmalarni qaytaradi. Status bo'yicha filterlash mumkin.
    """
    permission_classes = [IsAuthenticated, IsDeliveryRole] # Faqat delivery role uchun

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status (pending, preparing, ready, served)", type=openapi.TYPE_STRING, required=False)
        ],
        responses={200: DeliverySerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        queryset = Delivery.objects.filter(assigned_to=user).order_by('-created_at')

        # Status bo'yicha filterlash
        status_param = request.query_params.get('status', None)
        if status_param and status_param in dict(Delivery.STATUS_CHOICES):
             queryset = queryset.filter(status=status_param)
        elif status_param:
             # Agar status noto'g'ri kiritilsa
             return Response({"error": f"'{status_param}' status mavjud emas."}, status=status.HTTP_400_BAD_REQUEST)


        # Frontend talabiga ko'ra guruhlash kerak bo'lsa:
        # ready_deliveries = queryset.filter(status='ready')
        # delivering_deliveries = queryset.filter(status='preparing') # Yoki yangi status 'delivering'
        # served_deliveries = queryset.filter(status='served')
        #
        # ready_serializer = DeliverySerializer(ready_deliveries, many=True)
        # delivering_serializer = DeliverySerializer(delivering_deliveries, many=True)
        # served_serializer = DeliverySerializer(served_deliveries, many=True)
        #
        # return Response({
        #     'ready': ready_serializer.data,
        #     'delivering': delivering_serializer.data, # Frontend qanday kutayotganiga qarab nomlash
        #     'served': served_serializer.data
        # })

        # Hozircha oddiy list qaytaramiz, frontend o'zi guruhlaydi
        serializer = DeliverySerializer(queryset, many=True)
        return Response(serializer.data)


# ServedOrdersView o'zgarishsiz qolishi mumkin
class ServedOrdersView(APIView):
    permission_classes = [IsAuthenticated] # Yoki Adminlar uchun

    def get(self, request):
        # Ma'lum bir vaqt oralig'idagi 'served' buyurtmalarni olish mantiqan to'g'riroq
        # Masalan, oxirgi 24 soatdagilar
        # today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
        # orders = Order.objects.filter(status='served', created_at__gte=today_start)
        # takeouts = Takeout.objects.filter(status='served', created_at__gte=today_start)
        # deliveries = Delivery.objects.filter(status='served', created_at__gte=today_start)

        # Hozircha barcha 'served' larni olamiz
        orders = Order.objects.filter(status='served').order_by('-created_at')
        takeouts = Takeout.objects.filter(status='served').order_by('-created_at')
        deliveries = Delivery.objects.filter(status='served').order_by('-created_at')

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