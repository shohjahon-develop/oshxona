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
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}, 'total_price': {'read_only': True}}

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0
        for item_data in items_data:
            order_item = OrderItem.objects.create(order=order, **item_data)
            total_price += order_item.quantity * order_item.price
        order.total_price = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.items.all().delete()
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        total_price = 0
        if items_data:
            for item_data in items_data:
                order_item = OrderItem.objects.create(order=instance, **item_data)
                total_price += order_item.quantity * order_item.price
        instance.total_price = total_price
        instance.save()
        return instance

class TakeoutSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Takeout
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Delivery
        fields = '__all__'