from rest_framework import serializers
from django.core.validators import RegexValidator

from users.models import CustomerDelivery, Customer, User, Setting


class LoginSerializer(serializers.Serializer):
    pin_code = serializers.CharField(required=True, help_text="PIN kod")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    phone_regex = RegexValidator(
        regex=r'^\+998\d{9}$',
        message="Telefon raqami +998 bilan boshlanishi va 12 ta belgidan iborat bo‘lishi kerak."
    )
    phone = serializers.CharField(validators=[phone_regex], max_length=13)
    name = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = Customer
        fields = '__all__'

    def validate_name(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Ismda raqam bo‘lishi mumkin emas.")
        return value

class CustomerDeliverySerializer(serializers.ModelSerializer):
    phone_regex = RegexValidator(
        regex=r'^\+998\d{9}$',
        message="Telefon raqami +998 bilan boshlanishi va 12 ta belgidan iborat bo‘lishi kerak."
    )
    phone = serializers.CharField(validators=[phone_regex], max_length=13)
    name = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = CustomerDelivery
        fields = '__all__'

    def validate_name(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Ismda raqam bo‘lishi mumkin emas.")
        return value


class DashboardSummarySerializer(serializers.Serializer):
    today_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    today_sales_change_percent = serializers.CharField(max_length=10)
    today_orders_count = serializers.IntegerField()
    today_orders_change_percent = serializers.CharField(max_length=10)
    average_check = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_check_change_percent = serializers.CharField(max_length=10)
    active_staff_count = serializers.IntegerField()
    active_staff_change_percent = serializers.CharField(max_length=10)

class WeeklySalesSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField(max_length=3)) # Hafta kunlari qisqartmasi (Du, Se...)
    sales_data = serializers.ListField(child=serializers.DecimalField(max_digits=15, decimal_places=2))

class TopProductSerializer(serializers.Serializer):
    product_name = serializers.CharField(source='menu_item__name') # Corrected source
    quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)

class RecentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField(max_length=20) # 'Shu yerda', 'Olib ketish', 'Yetkazib berish'
    customer_display = serializers.CharField(max_length=100) # "Stol 3" yoki "Alisher (+998...)" yoki "Dilshod (+998...)"
    item_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField(max_length=50) # Statusning tarjimasi (Yakunlangan, Tayyorlanmoqda...)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M") # Formatni frontendga moslash


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            'id', 'restaurant_name', 'phone_number', 'email', 'address',
            'description', 'currency', 'language',
            'tax_rate', 'service_charge' # Qo'shilgan maydonlar
        ]
