from rest_framework import serializers
from django.core.validators import RegexValidator

from users.models import CustomerDelivery, Customer


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