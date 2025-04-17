# orders/serializers.py
from rest_framework import serializers
from menu.models import MenuItem
from users.models import Customer, CustomerDelivery, User
from .models import *
# Endi nested serializerlar kerak emas (MenuItemSerializer, CustomerSerializer va hk)

class TableSerializer(serializers.ModelSerializer):
    place_display = serializers.CharField(source='get_place_display', read_only=True)
    class Meta:
        model = Table
        fields = ['id', 'number', 'is_occupied', 'place', 'place_display']

# --- Item Serializerlar (ID larga qaytish) ---
class OrderItemSerializer(serializers.ModelSerializer):
    # Faqat ID orqali bog'lanish
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    # menu_item_id = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), source='menu_item', write_only=True) # Bu kerak emas, yuqoridagi yetarli

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity'] # item_total olib tashlandi
        read_only_fields = ['id']

class TakeoutItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = TakeoutItem
        fields = ['id', 'menu_item', 'quantity']
        read_only_fields = ['id']

class DeliveryItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = DeliveryItem
        fields = ['id', 'menu_item', 'quantity']
        read_only_fields = ['id']

# --- Order, Takeout, Delivery Serializerlar (Soddalashtirilgan) ---

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    # table_details olib tashlandi, faqat table (ID) qoladi
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all()) # read_only=False (default)
    status_display = serializers.CharField(source='get_status_display', read_only=True) # Bu qulay, qoldiramiz

    class Meta:
        model = Order
        fields = [
            'id', 'table', 'status', 'status_display',
            'total_price', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_price', 'status_display']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0
        order_items = []
        # Yaratish uchun items_data ichida {menu_item: <MenuItem instance>, quantity: X} bo'lishi kutiladi
        # yoki {menu_item_id: <ID>, quantity: X}
        for item_data in items_data:
            # Agar PrimaryKeyRelatedField ishlatilsa, menu_item object bo'ladi
            menu_item_obj = item_data['menu_item']
            quantity = item_data['quantity']
            order_items.append(OrderItem(order=order, menu_item=menu_item_obj, quantity=quantity))
            total_price += quantity * menu_item_obj.price # Narxni o'qish

        OrderItem.objects.bulk_create(order_items)
        order.total_price = total_price
        order.save()
        return order

    # Update metodi kerak bo'lsa qoldiriladi, lekin asosan status uchun action ishlatiladi
    # def update(self, instance, validated_data):
    #     instance.status = validated_data.get('status', instance.status)
    #     instance.save()
    #     return instance

class TakeoutSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    # customer (nested) olib tashlandi
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), required=False, allow_null=True # ID orqali bog'lanadi
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Takeout
        fields = [
            'id', 'customer', 'status', 'status_display',
            'total_price', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_price', 'status_display']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        takeout = Takeout.objects.create(**validated_data) # customer ID orqali keladi
        total_price = 0
        takeout_items = []
        for item_data in items_data:
            menu_item_obj = item_data['menu_item']
            quantity = item_data['quantity']
            takeout_items.append(TakeoutItem(takeout=takeout, menu_item=menu_item_obj, quantity=quantity))
            total_price += quantity * menu_item_obj.price

        TakeoutItem.objects.bulk_create(takeout_items)
        takeout.total_price = total_price
        takeout.save()
        return takeout

class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True)
    # customer (nested) olib tashlandi
    customer = serializers.PrimaryKeyRelatedField(
        queryset=CustomerDelivery.objects.all(), required=False, allow_null=True # ID orqali bog'lanadi
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)


    class Meta:
        model = Delivery
        fields = [
            'id', 'customer', 'status', 'status_display',
            'total_price', 'items', 'created_at' # assigned_to olib tashlandi
        ]
        read_only_fields = [
            'id', 'created_at', 'total_price', 'status_display'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # assigned_to logikasi olib tashlandi
        delivery = Delivery.objects.create(**validated_data) # customer ID orqali keladi
        total_price = 0
        delivery_items = []
        for item_data in items_data:
            menu_item_obj = item_data['menu_item']
            quantity = item_data['quantity']
            delivery_items.append(DeliveryItem(delivery=delivery, menu_item=menu_item_obj, quantity=quantity))
            total_price += quantity * menu_item_obj.price

        DeliveryItem.objects.bulk_create(delivery_items)
        delivery.total_price = total_price
        delivery.save()
        return delivery
# 996700720
# --- Statusni yangilash uchun Serializerlar (o'zgarishsiz qoladi) ---
class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

class TakeoutStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Takeout.STATUS_CHOICES)

class DeliveryStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Delivery.STATUS_CHOICES)

# DeliveryAssignSerializer kerak emas
# class DeliveryAssignSerializer(serializers.Serializer):
#     ...













# from rest_framework import serializers
# from menu.models import MenuItem
# from users.models import Customer, CustomerDelivery
# from .models import *
#
#
# class TableSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Table
#         fields = '__all__'
#
# class OrderItemSerializer(serializers.ModelSerializer):
#     menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
#
#     class Meta:
#         model = OrderItem
#         fields = ['menu_item', 'quantity']
#
# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)
#     table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())
#
#     class Meta:
#         model = Order
#         fields = ['id', 'table', 'status', 'total_price', 'items', 'created_at']
#         read_only_fields = ['id', 'created_at', 'total_price']
#
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         order = Order.objects.create(**validated_data)
#
#         order_items = [OrderItem(order=order, **item) for item in items_data]
#         OrderItem.objects.bulk_create(order_items)
#
#         order.calculate_total_price()
#         return order
#
# class TakeoutItemSerializer(serializers.ModelSerializer):
#     menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
#
#     class Meta:
#         model = TakeoutItem
#         fields = ['menu_item', 'quantity']
#
# class TakeoutSerializer(serializers.ModelSerializer):
#     items = TakeoutItemSerializer(many=True)
#     customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)
#
#     class Meta:
#         model = Takeout
#         fields = ['id', 'customer', 'status', 'total_price', 'items', 'created_at']
#         read_only_fields = ['id', 'created_at', 'total_price']
#
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         takeout = Takeout.objects.create(**validated_data)
#
#         takeout_items = [TakeoutItem(takeout=takeout, **item) for item in items_data] #bu kodni o'zgartirdim
#         TakeoutItem.objects.bulk_create(takeout_items)
#
#         takeout.calculate_total_price()
#         return takeout
#
#     def update(self, instance, validated_data):
#         instance.status = validated_data.get('status', instance.status)
#         instance.save()
#         return instance
#
# class DeliveryItemSerializer(serializers.ModelSerializer):
#     menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
#
#     class Meta:
#         model = DeliveryItem
#         fields = ['menu_item', 'quantity']
#
# class DeliverySerializer(serializers.ModelSerializer):
#     items = DeliveryItemSerializer(many=True)
#     customer = serializers.PrimaryKeyRelatedField(queryset=CustomerDelivery.objects.all(), required=False)
#
#     class Meta:
#         model = Delivery
#         fields = ['id', 'customer', 'status', 'total_price', 'items', 'created_at']
#         read_only_fields = ['id', 'created_at', 'total_price']
#
#     def update(self, instance, validated_data):
#         instance.status = validated_data.get('status', instance.status)
#         instance.save()
#         return instance
#
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         delivery = Delivery.objects.create(**validated_data)
#
#         delivery_items = [DeliveryItem(delivery=delivery, **item) for item in items_data] #order o'rniga delivery deb o'zgartiramiz!
#         DeliveryItem.objects.bulk_create(delivery_items)
#
#         delivery.calculate_total_price()
#         return delivery