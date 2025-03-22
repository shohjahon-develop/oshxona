from rest_framework import serializers
from .models import Table, Order, OrderItem, Takeout, Delivery, TakeoutItem, DeliveryItem


class TableSerializer(serializers.ModelSerializer):
    is_occupied = serializers.BooleanField(required=False)
    class Meta:
        model = Table
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class TakeoutItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeoutItem
        fields = '__all__'

class DeliveryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # ✅ total_price faqat o‘qish uchun

    class Meta:
        model = Order
        fields = '__all__'

class TakeoutSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Takeout
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Delivery
        fields = '__all__'