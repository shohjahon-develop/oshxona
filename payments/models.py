from django.db import models
from orders.models import Order

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)  # False = To‘lanmadi, True = To‘landi
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order.id} - {'To‘landi' if self.status else 'To‘lanmadi'}"
