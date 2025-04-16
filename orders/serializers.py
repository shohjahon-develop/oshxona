# orders/serializers.py
from rest_framework import serializers
from menu.models import MenuItem
from users.models import Customer, CustomerDelivery, User
from .models import *
from menu.serializers import MenuItemSerializer # Import MenuItemSerializer
from users.serializers import CustomerSerializer, CustomerDeliverySerializer, UserSerializer # Import kerakli user serializerlar

class TableSerializer(serializers.ModelSerializer):
    place_display = serializers.CharField(source='get_place_display', read_only=True)
    class Meta:
        model = Table
        fields = ['id', 'number', 'is_occupied', 'place', 'place_display']

# --- OrderItem, TakeoutItem, DeliveryItem uchun o'zgarish ---
class OrderItemSerializer(serializers.ModelSerializer):
    # O'qish uchun: To'liq MenuItem ma'lumotlari
    menu_item = MenuItemSerializer(read_only=True)
    # Yozish uchun: Faqat MenuItem ID si
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='menu_item', write_only=True
    )
    item_total = serializers.SerializerMethodField() # Har bir item uchun umumiy narx

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'item_total']
        read_only_fields = ['id', 'item_total']

    def get_item_total(self, obj):
        return obj.quantity * obj.menu_item.price

class TakeoutItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='menu_item', write_only=True
    )
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = TakeoutItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'item_total']
        read_only_fields = ['id', 'item_total']

    def get_item_total(self, obj):
        return obj.quantity * obj.menu_item.price

class DeliveryItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='menu_item', write_only=True
    )
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'item_total']
        read_only_fields = ['id', 'item_total']

    def get_item_total(self, obj):
        return obj.quantity * obj.menu_item.price

# --- Order, Takeout, Delivery Serializerlar uchun o'zgarish ---

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    table_details = TableSerializer(source='table', read_only=True) # Stol ma'lumotlari
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True) # Status tarjimasi

    class Meta:
        model = Order
        fields = [
            'id', 'table', 'table_details', 'status', 'status_display',
            'total_price', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_price', 'status_display', 'table_details']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0
        order_items = []
        for item_data in items_data:
            menu_item = item_data['menu_item'] # write_only=True bo'lgani uchun 'menu_item' keladi
            quantity = item_data['quantity']
            order_items.append(OrderItem(order=order, menu_item=menu_item, quantity=quantity))
            total_price += quantity * menu_item.price

        OrderItem.objects.bulk_create(order_items)
        order.total_price = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        # Statusni update qilish logikasi (agar kerak bo'lsa, action orqali qilish yaxshiroq)
        instance.status = validated_data.get('status', instance.status)
        # Boshqa maydonlarni ham update qilish mumkin
        instance.save()
        # Agar items o'zgarsa, narxni qayta hisoblash kerak bo'lishi mumkin
        return instance

class TakeoutSerializer(serializers.ModelSerializer):
    items = TakeoutItemSerializer(many=True)
    # O'qish uchun Customer ma'lumotlari
    customer = CustomerSerializer(read_only=True)
    # Yozish uchun Customer ID si (majburiy emas)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='customer',
        write_only=True, required=False, allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True) # Status tarjimasi

    class Meta:
        model = Takeout
        fields = [
            'id', 'customer', 'customer_id', 'status', 'status_display',
            'total_price', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_price', 'status_display', 'customer']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # customer_id orqali kelgan ma'lumotni customer ga o'tkazamiz
        customer = validated_data.pop('customer', None) # source='customer' ishlatilgani uchun
        takeout = Takeout.objects.create(customer=customer, **validated_data)

        total_price = 0
        takeout_items = []
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            takeout_items.append(TakeoutItem(takeout=takeout, menu_item=menu_item, quantity=quantity))
            total_price += quantity * menu_item.price

        TakeoutItem.objects.bulk_create(takeout_items)
        takeout.total_price = total_price
        takeout.save()
        return takeout

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True)
    # O'qish uchun CustomerDelivery ma'lumotlari
    customer = CustomerDeliverySerializer(read_only=True)
    # Yozish uchun CustomerDelivery ID si (majburiy emas)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomerDelivery.objects.all(), source='customer',
        write_only=True, required=False, allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True) # Status tarjimasi
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True) # Yetkazib beruvchi ma'lumotlari

    class Meta:
        model = Delivery
        fields = [
            'id', 'customer', 'customer_id', 'status', 'status_display',
            'total_price', 'items', 'created_at', 'assigned_to', 'assigned_to_details'
        ]
        read_only_fields = [
            'id', 'created_at', 'total_price', 'status_display',
            'customer', 'assigned_to_details'
        ]
        # `assigned_to` ni faqat adminlar yoki maxsus logikaga ko'ra o'zgartirish kerak bo'lishi mumkin
        # Hozircha `assigned_to` ni ham `write_only` qilmaymiz, lekin API viewda cheklash mumkin

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer = validated_data.pop('customer', None)
        # assigned_to ni ham pop qilish mumkin, agar create payti berilsa
        assigned_to = validated_data.pop('assigned_to', None)

        delivery = Delivery.objects.create(customer=customer, assigned_to=assigned_to, **validated_data)

        total_price = 0
        delivery_items = []
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            delivery_items.append(DeliveryItem(delivery=delivery, menu_item=menu_item, quantity=quantity))
            total_price += quantity * menu_item.price

        DeliveryItem.objects.bulk_create(delivery_items)
        delivery.total_price = total_price
        delivery.save()
        return delivery

    def update(self, instance, validated_data):
        # Faqat status va assigned_to ni yangilashga ruxsat beramiz (misol)
        instance.status = validated_data.get('status', instance.status)
        # Admin yoki manager rolidagilar tayinlashi uchun:
        # if request.user.role == 'admin': # Bu view ichida tekshiriladi
        instance.assigned_to = validated_data.get('assigned_to', instance.assigned_to)
        instance.save()
        return instance

# --- YANGI: Statusni yangilash uchun alohida serializer ---
class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

class TakeoutStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Takeout.STATUS_CHOICES)

class DeliveryStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Delivery.STATUS_CHOICES)

# --- YANGI: Yetkazib beruvchiga tayinlash uchun serializer ---
class DeliveryAssignSerializer(serializers.Serializer):
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='delivery', is_active=True),
        source='assigned_to', # Model field nomi
        allow_null=True # Tayinlovni olib tashlash uchun
    )

















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