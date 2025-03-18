from rest_framework import serializers
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone']


class CustomerDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDelivery
        fields = '__all__'