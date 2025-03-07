from django.utils.timezone import now, timedelta
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from orders.models import OrderItem
from payments.models import Payment

class RevenueStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = now().date()
        start_week = today - timedelta(days=today.weekday())  # Haftaning bosh kuni
        start_month = today.replace(day=1)  # Oyning bosh kuni
        start_year = today.replace(month=1, day=1)  # Yilning bosh kuni

        weekly_revenue = Payment.objects.filter(status=True, updated_at__date__gte=start_week).aggregate(Sum('order__total_price'))['order__total_price__sum'] or 0
        monthly_revenue = Payment.objects.filter(status=True, updated_at__date__gte=start_month).aggregate(Sum('order__total_price'))['order__total_price__sum'] or 0
        yearly_revenue = Payment.objects.filter(status=True, updated_at__date__gte=start_year).aggregate(Sum('order__total_price'))['order__total_price__sum'] or 0

        unpaid_orders = Payment.objects.filter(status=False).count()
        paid_orders = Payment.objects.filter(status=True).count()

        return Response({
            "weekly_revenue": weekly_revenue,
            "monthly_revenue": monthly_revenue,
            "yearly_revenue": yearly_revenue,
            "paid_orders": paid_orders,
            "unpaid_orders": unpaid_orders
        })



class ProductStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        top_products = OrderItem.objects.values('product__name').annotate(total_sold=Count('id')).order_by('-total_sold')[:5]
        least_sold_products = OrderItem.objects.values('product__name').annotate(total_sold=Count('id')).order_by('total_sold')[:5]

        return Response({
            "top_selling": list(top_products),
            "least_selling": list(least_sold_products)
        })