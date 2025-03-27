from rest_framework import serializers
from menu.models import MenuItem
from users.models import Customer, CustomerDelivery
from .models import *


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'table', 'status', 'total_price', 'items', 'created_at']
        read_only_fields = ['id', 'created_at', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        order_items = [OrderItem(order=order, **item) for item in items_data]
        OrderItem.objects.bulk_create(order_items)

        order.calculate_total_price()
        return order

class TakeoutItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = TakeoutItem
        fields = ['menu_item', 'quantity']

class TakeoutSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)

    class Meta:
        model = Takeout
        fields = ['id', 'customer', 'status', 'total_price', 'items', 'created_at']
        read_only_fields = ['id', 'created_at', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        takeout = Takeout.objects.create(**validated_data)

        takeout_items = [TakeoutItem(takeout=takeout, **item) for item in items_data] #bu kodni o'zgartirdim
        TakeoutItem.objects.bulk_create(takeout_items)

        takeout.calculate_total_price()
        return takeout

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class DeliveryItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = DeliveryItem
        fields = ['menu_item', 'quantity']

class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=CustomerDelivery.objects.all(), required=False)

    class Meta:
        model = Delivery
        fields = ['id', 'customer', 'status', 'total_price', 'items', 'created_at']
        read_only_fields = ['id', 'created_at', 'total_price']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        delivery = Delivery.objects.create(**validated_data)

        delivery_items = [DeliveryItem(delivery=delivery, **item) for item in items_data] #order o'rniga delivery deb o'zgartiramiz!
        DeliveryItem.objects.bulk_create(delivery_items)

        delivery.calculate_total_price()
        return delivery