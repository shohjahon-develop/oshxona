from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils.timezone import now
from datetime import timedelta
from .serializers import OrderStatisticsSerializer, PopularDishesSerializer, StaffActivitySerializer
from orders.models import Order # Order va Payment modellari qaysi app ichida bo‘lsa, o‘sha joydan import qilish kerak
from payments.models import Payment

class OrderStatisticsView(APIView):
    """Restoran buyurtma va to‘lov statistikasi"""

    def get(self, request):
        today = now()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        last_year = today - timedelta(days=365)

        total_orders = Order.objects.count()
        completed_orders = Order.objects.filter(status="served").count()
        pending_orders = Order.objects.exclude(status="served").count()

        paid_orders = Payment.objects.filter(status=True).count()
        unpaid_orders = Payment.objects.filter(status=False).count()

        total_revenue = Payment.objects.filter(status=True).aggregate(Sum("order__table__id"))["order__table__id__sum"] or 0

        data = {
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "paid_orders": paid_orders,
            "unpaid_orders": unpaid_orders,
            "total_revenue": total_revenue,
        }

        serializer = OrderStatisticsSerializer(data)
        return Response(serializer.data)

class PopularDishesView(APIView):
    """Eng ko‘p buyurtma qilingan taomlar"""

    def get(self, request):
        from orders.models import OrderItem  # OrderItem modeli kerak bo‘ladi
        popular_dishes = (
            OrderItem.objects.values("dish__name")
            .annotate(total_count=Count("id"))
            .order_by("-total_count")[:3]
        )

        serializer = PopularDishesSerializer(popular_dishes, many=True)
        return Response(serializer.data)

class StaffActivityView(APIView):
    """Hodimlarning buyurtma bajarish faolligi"""

    def get(self, request):
        from users.models import User  # Staff modeli kerak
        staff_activity = (
            User.objects.values("name")
            .annotate(total_orders=Count("order"))
            .order_by("-total_orders")[:5]
        )

        serializer = StaffActivitySerializer(staff_activity, many=True)
        return Response(serializer.data)
