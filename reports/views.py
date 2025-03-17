from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils.timezone import now
from datetime import timedelta

from users.models import User
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
            OrderItem.objects.values("name")
            .annotate(total_count=Count("id"))
            .order_by("-total_count")[:3]
        )

        serializer = PopularDishesSerializer(popular_dishes, many=True)
        return Response(serializer.data)


class EmployeeActivityReport(APIView):
    permission_classes = [IsAdminUser]  # Faqat adminlar ko‘rishi mumkin

    def get(self, request):
        # Faqat hodim bo‘lgan userlarni olish
        employees = User.objects.filter(role__in=["waiter", "chef", "cashier", "cleaner"])

        data = []

        for employee in employees:
            # Hodim bajargan buyurtmalar soni
            orders_count = Order.objects.filter(assigned_to=employee).count()

            # Hodim tomonidan bajarilgan buyurtmalar bo‘yicha tushum
            total_revenue = \
            Order.objects.filter(assigned_to=employee, status="completed").aggregate(Sum("total_price"))[
                "total_price__sum"] or 0

            # Hodimning oxirgi aktivligi
            last_active = employee.last_login if employee.last_login else "Ma’lumot yo‘q"

            data.append({
                "employee_id": employee.id,
                "full_name": f"{employee.first_name} {employee.last_name}",
                "role": employee.role,  # Hodimning roli (oshpaz, kassir va h.k.)
                "orders_count": orders_count,
                "total_revenue": total_revenue,
                "last_active": last_active
            })

        return Response({"employees": data})
