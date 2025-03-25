from rest_framework import serializers
from django.db.models import Count, Sum

class OrderStatisticsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    paid_orders = serializers.IntegerField()
    unpaid_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

class PopularDishesSerializer(serializers.Serializer):
    dish_name = serializers.CharField(source='menu_item__name') #изменил эту строчку
    total_count = serializers.IntegerField()

class StaffActivitySerializer(serializers.Serializer):
    staff_name = serializers.CharField()
    total_orders = serializers.IntegerField()