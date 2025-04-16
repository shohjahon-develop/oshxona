# reports/views.py
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DecimalField, Case, When, Value, CharField, Max, Min
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear, Coalesce
from django.utils.timezone import now, timedelta
from collections import defaultdict
import calendar

from users.models import User
from orders.models import Order, OrderItem, Takeout, TakeoutItem, Delivery, DeliveryItem, Table
from menu.models import MenuItem
from payments.models import Payment # Agar ishlatilsa
from .serializers import (
    OrderStatisticsSerializer, PopularDishesSerializer, StaffActivitySerializer,
    DashboardSummarySerializer, WeeklySalesSerializer, TopProductSerializer, RecentOrderSerializer,
    ReportPeriodSerializer, ProductReportSerializer, StaffReportSerializer, CustomerReportSerializer
)
from orders.serializers import OrderSerializer, TakeoutSerializer, DeliverySerializer # Recent Orders uchun

# --- Helper function ---
def calculate_percentage_change(current, previous):
    if previous is None or previous == 0:
        if current > 0:
            return "+inf%" # Yoki "+100%" yoki boshqa belgi
        return "0.0%" # O'zgarish yo'q
    change = ((current - previous) / previous) * 100
    return f"{change:+.1f}%"

# --- Dashboard API Views ---

class DashboardSummaryView(APIView):
    """Admin Dashboard uchun asosiy ko'rsatkichlar."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = now().date()
        yesterday = today - timedelta(days=1)

        # Bugungi savdo va buyurtmalar
        today_orders = Order.objects.filter(created_at__date=today, status='served')
        today_takeouts = Takeout.objects.filter(created_at__date=today, status='served')
        today_deliveries = Delivery.objects.filter(created_at__date=today, status='served')

        today_sales_orders = today_orders.aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
        today_sales_takeouts = today_takeouts.aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
        today_sales_deliveries = today_deliveries.aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
        today_total_sales = today_sales_orders + today_sales_takeouts + today_sales_deliveries

        today_orders_count = today_orders.count() + today_takeouts.count() + today_deliveries.count()

        # Kechagi savdo va buyurtmalar
        yesterday_orders = Order.objects.filter(created_at__date=yesterday, status='served')
        yesterday_takeouts = Takeout.objects.filter(created_at__date=yesterday, status='served')
        yesterday_deliveries = Delivery.objects.filter(created_at__date=yesterday, status='served')

        yesterday_sales_orders = yesterday_orders.aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
        yesterday_sales_takeouts = yesterday_takeouts.aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
        yesterday_sales_deliveries = yesterday_deliveries.aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
        yesterday_total_sales = yesterday_sales_orders + yesterday_sales_takeouts + yesterday_sales_deliveries

        yesterday_orders_count = yesterday_orders.count() + yesterday_takeouts.count() + yesterday_deliveries.count()

        # O'rtacha chek
        today_average_check = today_total_sales / today_orders_count if today_orders_count > 0 else 0
        yesterday_average_check = yesterday_total_sales / yesterday_orders_count if yesterday_orders_count > 0 else 0

        # Faol xodimlar (masalan, bugun login qilganlar yoki buyurtma bajarganlar)
        # Eng oddiy variant: 'is_active=True' bo'lgan xodimlar soni
        active_staff_count = User.objects.filter(is_staff=False, is_superuser=False, is_active=True).exclude(role='admin').count()
        # Kechagi faol xodimlar sonini hisoblash murakkabroq, soddalashtiramiz
        # yesterday_active_staff_count = ...

        data = {
            "today_sales": today_total_sales,
            "today_sales_change_percent": calculate_percentage_change(today_total_sales, yesterday_total_sales),
            "today_orders_count": today_orders_count,
            "today_orders_change_percent": calculate_percentage_change(today_orders_count, yesterday_orders_count),
            "average_check": today_average_check,
            "average_check_change_percent": calculate_percentage_change(today_average_check, yesterday_average_check),
            "active_staff_count": active_staff_count,
            # "active_staff_change_percent": "+0.0%" # Hozircha o'zgarish yo'q deb turamiz
        }
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)

class WeeklySalesView(APIView):
    """Haftalik savdo dinamikasi (oxirgi 7 kun)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday()) # Agar hafta Dushanbadan boshlansa
        # Yoki oxirgi 7 kun:
        start_date = today - timedelta(days=6)
        dates = [(start_date + timedelta(days=i)) for i in range(7)]
        labels = [d.strftime('%a')[:2] for d in dates] # ['Du', 'Se', ...]
        sales_data = []

        for date in dates:
            daily_sales_orders = Order.objects.filter(created_at__date=date, status='served').aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
            daily_sales_takeouts = Takeout.objects.filter(created_at__date=date, status='served').aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
            daily_sales_deliveries = Delivery.objects.filter(created_at__date=date, status='served').aggregate(total=Coalesce(Sum('total_price'), 0.0))['total']
            total_daily_sales = daily_sales_orders + daily_sales_takeouts + daily_sales_deliveries
            sales_data.append(total_daily_sales)

        data = {
            "labels": labels,
            "sales_data": sales_data
        }
        serializer = WeeklySalesSerializer(data)
        return Response(serializer.data)

class TopProductsView(APIView):
    """Eng ko'p sotilgan mahsulotlar (kunlik, haftalik, oylik)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'weekly') # default 'weekly'
        limit = int(request.query_params.get('limit', 5)) # default 5 ta
        today = now().date()
        start_date = today

        if period == 'daily':
            start_date = today
        elif period == 'weekly':
            start_date = today - timedelta(days=6)
        elif period == 'monthly':
            start_date = today - timedelta(days=29)
        else: # Default weekly
            start_date = today - timedelta(days=6)

        # Barcha item turlarini birlashtirish (Union ishlatish mumkin, lekin ORM da murakkab)
        # Alternativa: Har birini alohida aggregate qilib, keyin birlashtirish
        order_items = OrderItem.objects.filter(order__created_at__date__gte=start_date, order__status='served')
        takeout_items = TakeoutItem.objects.filter(takeout__created_at__date__gte=start_date, takeout__status='served')
        delivery_items = DeliveryItem.objects.filter(delivery__created_at__date__gte=start_date, delivery__status='served')

        product_sales = defaultdict(lambda: {'quantity_sold': 0, 'total_revenue': 0.0})

        for item in order_items:
            product_sales[item.menu_item.name]['quantity_sold'] += item.quantity
            product_sales[item.menu_item.name]['total_revenue'] += float(item.quantity * item.menu_item.price)

        for item in takeout_items:
            product_sales[item.menu_item.name]['quantity_sold'] += item.quantity
            product_sales[item.menu_item.name]['total_revenue'] += float(item.quantity * item.menu_item.price)

        for item in delivery_items:
            product_sales[item.menu_item.name]['quantity_sold'] += item.quantity
            product_sales[item.menu_item.name]['total_revenue'] += float(item.quantity * item.menu_item.price)

        # Saralash (masalan, savdo bo'yicha)
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1]['total_revenue'], reverse=True)

        top_products_data = [
            {
                "product_name": name,
                "quantity_sold": data['quantity_sold'],
                "total_revenue": data['total_revenue']
            } for name, data in sorted_products[:limit]
        ]

        serializer = TopProductSerializer(top_products_data, many=True)
        return Response(serializer.data)


class RecentOrdersView(APIView):
    """Oxirgi buyurtmalar ro'yxati (limit bilan)."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 5))

        # Oxirgi N ta buyurtmani olish (hamma turlardan)
        # Buni samarali qilish uchun querylarni optimallashtirish kerak bo'lishi mumkin
        orders = Order.objects.all().order_by('-created_at')[:limit]
        takeouts = Takeout.objects.all().order_by('-created_at')[:limit]
        deliveries = Delivery.objects.all().order_by('-created_at')[:limit]

        combined_list = []
        for order in orders:
            combined_list.append({
                "id": order.id,
                "type": "Shu yerda",
                "customer_display": f"Stol {order.table.number}",
                "item_count": order.items.count(), # Yoki quantity summasi?
                "total_amount": order.total_price,
                "status": order.status, # Keyin serializerda tarjima qilinadi
                "status_display": order.get_status_display(),
                "created_at": order.created_at
            })
        for takeout in takeouts:
             combined_list.append({
                 "id": takeout.id,
                 "type": "Olib ketish",
                 "customer_display": f"{takeout.customer.name if takeout.customer else "Noma'lum"}",
                 "item_count": takeout.items.count(),
                 "total_amount": takeout.total_price,
                 "status": takeout.status,
                 "status_display": takeout.get_status_display(),
                 "created_at": takeout.created_at
             })
        for delivery in deliveries:
             combined_list.append({
                 "id": delivery.id,
                 "type": "Yetkazib berish",
                 "customer_display": f"{delivery.customer.name if delivery.customer else 'Noma\'lum'}",
                 "item_count": delivery.items.count(),
                 "total_amount": delivery.total_price,
                 "status": delivery.status,
                 "status_display": delivery.get_status_display(),
                 "created_at": delivery.created_at
             })

        # Oxirgi yaratilganlar bo'yicha saralash
        combined_list.sort(key=lambda x: x['created_at'], reverse=True)

        # Faqat limitdagilarni olish
        recent_orders_data = combined_list[:limit]

        # Serializer ishlatishda ehtiyot bo'lish kerak, chunki data generic
        # Biz o'zimiz dict yaratganimiz uchun, RecentOrderSerializer ni to'g'ridan-to'g'ri ishlatishimiz mumkin
        serializer = RecentOrderSerializer(recent_orders_data, many=True)
        return Response(serializer.data)


# --- Hisobotlar Sahifasi API Views ---

class GeneralReportView(APIView):
    """Hisobotlar sahifasi uchun umumiy savdo hisoboti."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'weekly') # daily, weekly, monthly, yearly
        today = now().date()
        start_date = today
        end_date = today

        if period == 'daily':
            start_date = today
            period_name = 'Kunlik'
            trunc_func = TruncDay
            date_format = '%H:%M' # Soat bo'yicha dinamika
            dynamics_label_format = lambda d: d.strftime('%H:00')
            dynamics_range = [today + timedelta(hours=i) for i in range(24)]

        elif period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            period_name = 'Haftalik'
            trunc_func = TruncDay
            dynamics_label_format = lambda d: d.strftime('%a') # Hafta kunlari
            dynamics_range = [start_date + timedelta(days=i) for i in range(7)]

        elif period == 'monthly':
            start_date = today.replace(day=1)
            _, last_day = calendar.monthrange(today.year, today.month)
            end_date = today.replace(day=last_day)
            period_name = 'Oylik'
            trunc_func = TruncDay # Kun bo'yicha dinamika
            dynamics_label_format = lambda d: d.strftime('%d') # Kun raqami
            dynamics_range = [start_date + timedelta(days=i) for i in range(last_day)]

        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            period_name = 'Yillik'
            trunc_func = TruncMonth # Oy bo'yicha dinamika
            dynamics_label_format = lambda d: d.strftime('%b') # Oy nomi
            dynamics_range = [start_date.replace(month=m) for m in range(1, 13)]

        else:
            return Response({"error": "Noto'g'ri period"}, status=status.HTTP_400_BAD_REQUEST)

        # Umumiy savdo, buyurtmalar soni, o'rtacha chek
        orders_q = Order.objects.filter(created_at__date__range=(start_date, end_date), status='served')
        takeouts_q = Takeout.objects.filter(created_at__date__range=(start_date, end_date), status='served')
        deliveries_q = Delivery.objects.filter(created_at__date__range=(start_date, end_date), status='served')

        total_sales = (orders_q.aggregate(s=Coalesce(Sum('total_price'), 0.0))['s'] +
                       takeouts_q.aggregate(s=Coalesce(Sum('total_price'), 0.0))['s'] +
                       deliveries_q.aggregate(s=Coalesce(Sum('total_price'), 0.0))['s'])

        total_orders_count = orders_q.count() + takeouts_q.count() + deliveries_q.count()
        average_check = total_sales / total_orders_count if total_orders_count > 0 else 0

        # Savdo dinamikasi
        sales_dynamics_data = defaultdict(float)
        all_sales = list(orders_q) + list(takeouts_q) + list(deliveries_q)
        for sale in all_sales:
            # Davrga qarab trunc_func ni qo'llash kerak
            # Bu qismni optimallashtirish uchun DB darajasida group by qilish yaxshiroq
            dt_key = sale.created_at.date() # Eng oddiy, kun bo'yicha
            if period == 'yearly':
                 dt_key = sale.created_at.date().replace(day=1) # Oyning birinchi kuni
            elif period == 'daily':
                 dt_key = sale.created_at.replace(minute=0, second=0, microsecond=0) # Soat

            sales_dynamics_data[dt_key] += float(sale.total_price)

        dynamics_labels = [dynamics_label_format(d) for d in dynamics_range]
        dynamics_values = [sales_dynamics_data.get(d.date() if period != 'daily' else d, 0.0) for d in dynamics_range]


        # Buyurtma turlari
        order_types_count = {
            'Shu yerda': orders_q.count(),
            'Olib ketish': takeouts_q.count(),
            'Yetkazib berish': deliveries_q.count()
        }
        order_types_percent = {
            k: (v / total_orders_count * 100) if total_orders_count > 0 else 0
            for k, v in order_types_count.items()
        }

        report_data = {
            "period": period_name,
            "total_sales": total_sales,
            "total_orders": total_orders_count,
            "average_check": average_check,
            "sales_dynamics": {"labels": dynamics_labels, "data": dynamics_values},
            "order_types": {
                'Shu yerda': {'percent': f"{order_types_percent['Shu yerda']:.1f}%", 'count': order_types_count['Shu yerda']},
                'Olib ketish': {'percent': f"{order_types_percent['Olib ketish']:.1f}%", 'count': order_types_count['Olib ketish']},
                'Yetkazib berish': {'percent': f"{order_types_percent['Yetkazib berish']:.1f}%", 'count': order_types_count['Yetkazib berish']},
            }
            # Payment methods uchun Payment modelini tahlil qilish kerak
        }

        serializer = ReportPeriodSerializer(report_data)
        return Response(serializer.data)

class ProductReportView(APIView):
    """Mahsulotlar bo'yicha hisobot."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'weekly') # daily, weekly, monthly, yearly
        today = now().date()
        start_date = today

        if period == 'daily':
            start_date = today
        elif period == 'weekly':
            start_date = today - timedelta(days=6)
        elif period == 'monthly':
            start_date = today - timedelta(days=29)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
        else: # Default weekly
            start_date = today - timedelta(days=6)

        # Barcha itemlarni aggregate qilish
        order_items_agg = OrderItem.objects.filter(order__created_at__date__gte=start_date, order__status='served') \
                           .values('menu_item__name') \
                           .annotate(
                               quantity_sold=Sum('quantity'),
                               total_revenue=Sum(F('quantity') * F('menu_item__price'))
                           ).order_by('-total_revenue')

        takeout_items_agg = TakeoutItem.objects.filter(takeout__created_at__date__gte=start_date, takeout__status='served') \
                            .values('menu_item__name') \
                            .annotate(
                                quantity_sold=Sum('quantity'),
                                total_revenue=Sum(F('quantity') * F('menu_item__price'))
                            )

        delivery_items_agg = DeliveryItem.objects.filter(delivery__created_at__date__gte=start_date, delivery__status='served') \
                             .values('menu_item__name') \
                             .annotate(
                                 quantity_sold=Sum('quantity'),
                                 total_revenue=Sum(F('quantity') * F('menu_item__price'))
                             )

        # Natijalarni birlashtirish
        product_report_data = defaultdict(lambda: {'quantity_sold': 0, 'total_revenue': 0.0})
        for item in order_items_agg:
            name = item['menu_item__name']
            product_report_data[name]['quantity_sold'] += item['quantity_sold']
            product_report_data[name]['total_revenue'] += float(item['total_revenue'])
        for item in takeout_items_agg:
            name = item['menu_item__name']
            product_report_data[name]['quantity_sold'] += item['quantity_sold']
            product_report_data[name]['total_revenue'] += float(item['total_revenue'])
        for item in delivery_items_agg:
            name = item['menu_item__name']
            product_report_data[name]['quantity_sold'] += item['quantity_sold']
            product_report_data[name]['total_revenue'] += float(item['total_revenue'])

        # Listga o'tkazish va saralash
        final_report = [
            {"product_name": name, **data}
            for name, data in product_report_data.items()
        ]
        final_report.sort(key=lambda x: x['total_revenue'], reverse=True)


        serializer = ProductReportSerializer(final_report, many=True)
        return Response(serializer.data)


class StaffReportView(APIView):
    """Xodimlar bo'yicha hisobot."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'weekly')
        today = now().date()
        start_date = today

        if period == 'daily':
            start_date = today
        elif period == 'weekly':
            start_date = today - timedelta(days=6)
        elif period == 'monthly':
            start_date = today - timedelta(days=29)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
        else: # Default weekly
            start_date = today - timedelta(days=6)

        # Faqat xodimlarni olish (admin emas)
        staff = User.objects.filter(is_staff=False, is_superuser=False).exclude(role='admin')

        # Yetkazib beruvchilar uchun statistikani hisoblash
        delivery_stats = Delivery.objects.filter(
                assigned_to__in=staff,
                created_at__date__gte=start_date,
                status='served'
            ) \
            .values('assigned_to') \
            .annotate(
                completed_deliveries_count=Count('id'),
                total_delivery_sales=Sum('total_price'),
                avg_delivery_check=Avg('total_price')
            )

        delivery_stats_dict = {stat['assigned_to']: stat for stat in delivery_stats}

        staff_data = []
        for employee in staff:
            emp_data = StaffReportSerializer(employee).data # Asosiy ma'lumotlar
            stats = delivery_stats_dict.get(employee.id)
            if stats:
                 emp_data['completed_deliveries_count'] = stats['completed_deliveries_count']
                 emp_data['total_delivery_sales'] = stats['total_delivery_sales']
                 emp_data['avg_delivery_check'] = stats['avg_delivery_check']
            else:
                 emp_data['completed_deliveries_count'] = 0
                 emp_data['total_delivery_sales'] = 0.0
                 emp_data['avg_delivery_check'] = 0.0

            # Boshqa rollar uchun ham statistika qo'shish mumkin (masalan, kassir uchun to'lovlar)
            staff_data.append(emp_data)


        return Response(staff_data)


class CustomerReportView(APIView):
    """Mijozlar bo'yicha hisobot."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'weekly')
        today = now().date()
        start_date = today

        if period == 'daily':
            start_date = today
        elif period == 'weekly':
            start_date = today - timedelta(days=6)
        elif period == 'monthly':
            start_date = today - timedelta(days=29)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
        else: # Default weekly
            start_date = today - timedelta(days=6)

        # Har xil turdagi mijozlarni (Customer, CustomerDelivery) va stollarni (Order) olish
        orders_agg = Order.objects.filter(created_at__date__gte=start_date, status='served') \
                       .values('table__number') \
                       .annotate(
                           orders_count=Count('id'),
                           total_sales=Sum('total_price'),
                           last_order_date=Max('created_at'),
                           first_order_date=Min('created_at'),
                       )

        takeouts_agg = Takeout.objects.filter(created_at__date__gte=start_date, status='served') \
                        .values('customer__id', 'customer__name', 'customer__phone') \
                        .annotate(
                            orders_count=Count('id'),
                            total_sales=Sum('total_price'),
                            last_order_date=Max('created_at'),
                            first_order_date=Min('created_at'),
                        )

        deliveries_agg = Delivery.objects.filter(created_at__date__gte=start_date, status='served') \
                         .values('customer__id', 'customer__name', 'customer__phone', 'customer__address') \
                         .annotate(
                             orders_count=Count('id'),
                             total_sales=Sum('total_price'),
                             last_order_date=Max('created_at'),
                             first_order_date=Min('created_at'),
                         )

        customer_report_data = []

        # Stol buyurtmalari
        for item in orders_agg:
            count = item['orders_count']
            sales = item['total_sales']
            customer_report_data.append({
                "customer_id": None,
                "customer_name": f"Stol {item['table__number']}",
                "customer_phone": None,
                "customer_address": None,
                "order_type": "Shu yerda",
                "orders_count": count,
                "total_sales": sales,
                "average_check": sales / count if count else 0,
                "first_order_date": item['first_order_date'],
                "last_order_date": item['last_order_date'],
            })

        # Olib ketish buyurtmalari
        for item in takeouts_agg:
            count = item['orders_count']
            sales = item['total_sales']
            customer_report_data.append({
                "customer_id": item['customer__id'],
                "customer_name": item['customer__name'],
                "customer_phone": item['customer__phone'],
                "customer_address": None,
                "order_type": "Olib ketish",
                "orders_count": count,
                "total_sales": sales,
                "average_check": sales / count if count else 0,
                "first_order_date": item['first_order_date'],
                "last_order_date": item['last_order_date'],
            })

        # Yetkazib berish buyurtmalari
        for item in deliveries_agg:
            count = item['orders_count']
            sales = item['total_sales']
            customer_report_data.append({
                "customer_id": item['customer__id'],
                "customer_name": item['customer__name'],
                "customer_phone": item['customer__phone'],
                "customer_address": item['customer__address'],
                "order_type": "Yetkazib berish",
                "orders_count": count,
                "total_sales": sales,
                "average_check": sales / count if count else 0,
                "first_order_date": item['first_order_date'],
                "last_order_date": item['last_order_date'],
            })

        # Saralash (masalan, oxirgi buyurtma sanasi bo'yicha)
        customer_report_data.sort(key=lambda x: x['last_order_date'], reverse=True)

        serializer = CustomerReportSerializer(customer_report_data, many=True)
        return Response(serializer.data)


# Mavjud Viewlarni ham to'g'irlashimiz mumkin
class OrderStatisticsView(APIView):
    """Restoran buyurtma va to‘lov statistikasi (Soddalashtirilgan)"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Barcha davrlardagi statistika
        total_orders_q = Order.objects.all()
        total_takeouts_q = Takeout.objects.all()
        total_deliveries_q = Delivery.objects.all()

        completed_orders_q = Order.objects.filter(status="served")
        completed_takeouts_q = Takeout.objects.filter(status="served")
        completed_deliveries_q = Delivery.objects.filter(status="served")

        total_orders_count = total_orders_q.count() + total_takeouts_q.count() + total_deliveries_q.count()
        completed_orders_count = completed_orders_q.count() + completed_takeouts_q.count() + completed_deliveries_q.count()
        pending_orders_count = total_orders_count - completed_orders_count

        total_revenue = (completed_orders_q.aggregate(s=Coalesce(Sum('total_price'), 0.0))['s'] +
                         completed_takeouts_q.aggregate(s=Coalesce(Sum('total_price'), 0.0))['s'] +
                         completed_deliveries_q.aggregate(s=Coalesce(Sum('total_price'), 0.0))['s'])

        data = {
            "total_orders": total_orders_count,
            "completed_orders": completed_orders_count,
            "pending_orders": pending_orders_count,
            "total_revenue": total_revenue,
        }

        serializer = OrderStatisticsSerializer(data)
        return Response(serializer.data)

# PopularDishesView da o'zgartirish kerak emas, u TopProductsView ga o'xshash
# EmployeeActivityReport ni StaffReportView almashtiradi










# from rest_framework.permissions import IsAdminUser
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.db.models import Count, Sum
# from django.utils.timezone import now
# from datetime import timedelta
#
# from users.models import User
# from .serializers import OrderStatisticsSerializer, PopularDishesSerializer, StaffActivitySerializer
# from orders.models import Order # Order va Payment modellari qaysi app ichida bo‘lsa, o‘sha joydan import qilish kerak
# from payments.models import Payment
#
# class OrderStatisticsView(APIView):
#     """Restoran buyurtma va to‘lov statistikasi"""
#
#     def get(self, request):
#         today = now()
#         last_week = today - timedelta(days=7)
#         last_month = today - timedelta(days=30)
#         last_year = today - timedelta(days=365)
#
#         total_orders = Order.objects.count()
#         completed_orders = Order.objects.filter(status="served").count()
#         pending_orders = Order.objects.exclude(status="served").count()
#
#         paid_orders = Payment.objects.filter(status=True).count()
#         unpaid_orders = Payment.objects.filter(status=False).count()
#
#         total_revenue = Payment.objects.filter(status=True).aggregate(Sum("order__table__id"))["order__table__id__sum"] or 0
#
#         data = {
#             "total_orders": total_orders,
#             "completed_orders": completed_orders,
#             "pending_orders": pending_orders,
#             "paid_orders": paid_orders,
#             "unpaid_orders": unpaid_orders,
#             "total_revenue": total_revenue,
#         }
#
#         serializer = OrderStatisticsSerializer(data)
#         return Response(serializer.data)
#
# class PopularDishesView(APIView):
#     """Eng ko‘p buyurtma qilingan taomlar"""
#
#     def get(self, request):
#         from orders.models import OrderItem  # OrderItem modeli kerak bo‘ladi
#         popular_dishes = (
#             OrderItem.objects.values("menu_item__name")
#             .annotate(total_count=Count("id"))
#             .order_by("-total_count")[:3]
#         )
#
#         serializer = PopularDishesSerializer(popular_dishes, many=True)
#         return Response(serializer.data)
#
#
# class EmployeeActivityReport(APIView):
#     permission_classes = [IsAdminUser]  # Faqat adminlar ko‘rishi mumkin
#
#     def get(self, request):
#         # Faqat hodim bo‘lgan userlarni olish
#         employees = User.objects.filter(role__in=["waiter", "chef", "cashier", "cleaner"])
#
#         data = []
#
#         for employee in employees:
#             # Hodim bajargan buyurtmalar soni
#             orders_count = Order.objects.filter(assigned_to=employee).count()
#
#             # Hodim tomonidan bajarilgan buyurtmalar bo‘yicha tushum
#             total_revenue = \
#             Order.objects.filter(assigned_to=employee, status="completed").aggregate(Sum("total_price"))[
#                 "total_price__sum"] or 0
#
#             # Hodimning oxirgi aktivligi
#             last_active = employee.last_login if employee.last_login else "Ma’lumot yo‘q"
#
#             data.append({
#                 "employee_id": employee.id,
#                 "full_name": f"{employee.first_name} {employee.last_name}",
#                 "role": employee.role,  # Hodimning roli (oshpaz, kassir va h.k.)
#                 "orders_count": orders_count,
#                 "total_revenue": total_revenue,
#                 "last_active": last_active
#             })
#
#         return Response({"employees": data})