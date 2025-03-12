from rest_framework import serializers
from .models import Table, Order, OrderItem, Takeout, Delivery, TakeoutItem, DeliveryItem


class TableSerializer(serializers.ModelSerializer):
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
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'table', 'status', 'created_at', 'items']

class TakeoutSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Takeout
        fields = ['id', 'customer', 'status', 'created_at', 'items']


class DeliverySerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'customer', 'status', 'created_at', 'items']