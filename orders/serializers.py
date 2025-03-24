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

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        for item in items_data:
            OrderItem.objects.create(order=order, menu_item_id=item["menu_item"],
                                     quantity=item["quantity"])  # ✅ To‘g‘ri bog‘lanish

        order.calculate_total_price()  # ✅ Total narxni yangilash
        return order


class TakeoutSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)

    class Meta:
        model = Takeout
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        takeout = Takeout.objects.create(**validated_data)

        for item in items_data:
            TakeoutItem.objects.create(order=takeout, menu_item_id=item["menu_item"], quantity=item["quantity"])  # ✅ To‘g‘ri bog‘lanish

        takeout.calculate_total_price()  # ✅ Total narxni yangilash
        return takeout


class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True)

    class Meta:
        model = Delivery
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        delivery = Delivery.objects.create(**validated_data)

        for item in items_data:
            DeliveryItem.objects.create(order=delivery, menu_item_id=item["menu_item"], quantity=item["quantity"])  # ✅ To‘g‘ri bog‘lanish

        delivery.calculate_total_price()  # ✅ Total narxni yangilash
        return delivery
