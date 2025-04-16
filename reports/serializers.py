# reports/serializers.py
from rest_framework import serializers
from django.db.models import Count, Sum, Avg # Avg qo'shildi

from users.models import User


# Mavjud serializerlar yaxshi ko'rinadi, ularni ishlatamiz.
# Faqat PopularDishesSerializer va ProductReportSerializer dagi source ni tekshiramiz

class OrderStatisticsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    # Payment modeliga bog'liq bo'lganlar kerak bo'lmasligi mumkin,
    # chunki order statusi o'zi yetarli bo'lishi mumkin.
    # Agar payment alohida track qilinsa, qoldiramiz.
    # paid_orders = serializers.IntegerField()
    # unpaid_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2) # Umumiy daromad (served orderlar bo'yicha)

class PopularDishesSerializer(serializers.Serializer):
    # Agar OrderItem.menu_item.name bo'lsa, source to'g'ri.
    dish_name = serializers.CharField(source='menu_item__name')
    total_count = serializers.IntegerField()

class StaffActivitySerializer(serializers.Serializer):
    # Bu serializer EmployeeActivityReport uchun ishlatiladi,
    # lekin u Order.assigned_to ga bog'liq edi. Hozir User modeli orqali ishlashi kerak.
    staff_name = serializers.CharField() # User.name dan olinadi
    role = serializers.CharField()       # User.role dan olinadi
    # Buyurtmalar soni (agar waiter/chef bo'lsa - qaysi buyurtmani kim yaratgani/o'zgartirgani noaniq)
    # Yetkazib beruvchi uchun:
    deliveries_completed = serializers.IntegerField(required=False)
    # Kassir uchun (Payment modeliga bog'liq):
    # payments_processed = serializers.IntegerField(required=False)
    # Admin uchun:
    # actions_count = serializers.IntegerField(required=False)


# --- Admin Dashboard uchun asosiy serializerlar (users/serializers.py dan ko'chirilgan va to'ldirilgan) ---

class DashboardSummarySerializer(serializers.Serializer):
    today_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    today_sales_change_percent = serializers.CharField(max_length=10)
    today_orders_count = serializers.IntegerField()
    today_orders_change_percent = serializers.CharField(max_length=10)
    average_check = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_check_change_percent = serializers.CharField(max_length=10)
    active_staff_count = serializers.IntegerField()
    # active_staff_change_percent maydoni uchun logikani viewda qilish kerak
    # active_staff_change_percent = serializers.CharField(max_length=10)

class WeeklySalesSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    sales_data = serializers.ListField(child=serializers.DecimalField(max_digits=15, decimal_places=2))

class TopProductSerializer(serializers.Serializer):
    product_name = serializers.CharField() # Viewda annotate qilingan nomni ishlatamiz
    quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)

class RecentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField(max_length=20)
    customer_display = serializers.CharField(max_length=100)
    item_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField(max_length=50) # Faqat status kodini qaytaramiz
    # status_display olib tashlandi
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    # get_status_display ni qo'lda qo'shamiz, chunki bu generic serializer
    def get_status_display(self, obj):
        # obj bu dictionary bo'ladi viewdan kelganda
        status_code = obj.get('status')
        # Har bir model uchun status tanlovlarini olishimiz kerak
        all_status_choices = dict(Order.STATUS_CHOICES + Takeout.STATUS_CHOICES + Delivery.STATUS_CHOICES)
        return all_status_choices.get(status_code, status_code)


# --- Hisobotlar Sahifasi Uchun Serializerlar ---

class ReportPeriodSerializer(serializers.Serializer):
    period = serializers.CharField() # 'Kunlik', 'Haftalik', 'Oylik', 'Yillik'
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_orders = serializers.IntegerField()
    average_check = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)
    # total_profit = serializers.DecimalField(max_digits=15, decimal_places=2) # Foydani hisoblash uchun mahsulot tannarxi kerak
    sales_dynamics = serializers.DictField() # {'labels': [], 'data': []} - Kunlar/Haftalar/Oylar bo'yicha savdo
    # payment_methods = serializers.DictField() # {'Naqd': {'percent': %, 'amount': X}, 'Karta': ...} - Payment modeliga bog'liq
    order_types = serializers.DictField() # {'Shu yerda': {'percent': %, 'count': X}, 'Olib ketish': ..., 'Yetkazib berish': ...}

class ProductReportSerializer(serializers.Serializer):
    product_name = serializers.CharField() # Annotate qilingan nom
    quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    # profit = serializers.DecimalField(max_digits=15, decimal_places=2) # Tannarx kerak

class StaffReportSerializer(serializers.ModelSerializer): # User modelini ishlatamiz
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    # Yetkazib beruvchi statistikasi olib tashlandi
    # completed_deliveries_count = serializers.IntegerField(read_only=True, default=0)
    # total_delivery_sales = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, default=0)
    # avg_delivery_check = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, default=0)

    class Meta:
        model = User
        # Faqat asosiy ma'lumotlar qoldi
        fields = [
            'id', 'name', 'role', 'role_display', 'is_active', 'pin_code', 'phone' # phone ham qo'shildi
        ]
        read_only_fields = fields

class CustomerReportSerializer(serializers.Serializer):
    # customer_type = serializers.CharField() # 'Shu yerda', 'Olib ketish (Doimiy)', 'Olib ketish (Yangi)', 'Yetkazib berish'
    customer_id = serializers.IntegerField(allow_null=True)
    customer_name = serializers.CharField(allow_null=True)
    customer_phone = serializers.CharField(allow_null=True)
    customer_address = serializers.CharField(allow_null=True) # Faqat Delivery uchun
    order_type = serializers.CharField() # 'Shu yerda', 'Olib ketish', 'Yetkazib berish'
    orders_count = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_check = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)
    first_order_date = serializers.DateTimeField(allow_null=True)
    last_order_date = serializers.DateTimeField(allow_null=True)


# from rest_framework import serializers
# from django.db.models import Count, Sum
#
# class OrderStatisticsSerializer(serializers.Serializer):
#     total_orders = serializers.IntegerField()
#     completed_orders = serializers.IntegerField()
#     pending_orders = serializers.IntegerField()
#     paid_orders = serializers.IntegerField()
#     unpaid_orders = serializers.IntegerField()
#     total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
#
# class PopularDishesSerializer(serializers.Serializer):
#     dish_name = serializers.CharField(source='menu_item__name') #изменил эту строчку
#     total_count = serializers.IntegerField()
#
# class StaffActivitySerializer(serializers.Serializer):
#     staff_name = serializers.CharField()
#     total_orders = serializers.IntegerField()
#
#
#
# class ReportPeriodSerializer(serializers.Serializer):
#     period = serializers.CharField()
#     total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
#     total_orders = serializers.IntegerField()
#     average_check = serializers.DecimalField(max_digits=15, decimal_places=2)
#     total_profit = serializers.DecimalField(max_digits=15, decimal_places=2) # Foydani hisoblash logikasi kerak
#     sales_dynamics = serializers.DictField() # {'labels': [], 'data': []}
#     payment_methods = serializers.DictField() # {'cash': {'percent': %, 'amount': X}, ...}
#     order_types = serializers.DictField() # {'dine_in': {'percent': %, 'count': X}, ...}
#
# class ProductReportSerializer(serializers.Serializer):
#     product_name = serializers.CharField(source='menu_item__name')
#     quantity_sold = serializers.IntegerField()
#     total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
#     profit = serializers.DecimalField(max_digits=15, decimal_places=2) # Foydani hisoblash logikasi kerak
#
# class StaffReportSerializer(serializers.Serializer):
#     staff_name = serializers.CharField()
#     role = serializers.CharField()
#     orders_served = serializers.IntegerField() # Yoki "processed_payments" kassir uchun
#     total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
#     average_check = serializers.DecimalField(max_digits=15, decimal_places=2)
#     # last_active = serializers.DateTimeField(allow_null=True) # Agar kerak bo'lsa
#
# class CustomerReportSerializer(serializers.Serializer):
#     customer_type = serializers.CharField()
#     orders_count = serializers.IntegerField()
#     total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
#     average_check = serializers.DecimalField(max_digits=15, decimal_places=2)
