from django.db import models
from users.models import Customer,CustomerDelivery
from menu.models import MenuItem

class Table(models.Model):
    PLACE_CHOICE = [
        ('hall', 'Zall'),
        ('second floor', 'Ikkinchi qavat'),
        ('basement', 'Padval'),
    ]
    place = models.CharField(max_length=20,choices=PLACE_CHOICE,default='hall')
    number = models.PositiveIntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)  # Stol band yoki yo‘qligi

    def __str__(self):
        return f"Table {self.number}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutish jarayonida'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('served', 'Yakunlangan'),
    ]
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)  # Agar joyida yeyilsa
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class Takeout(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutish jarayonida'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('served', 'Yakunlangan'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutish jarayonida'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('served', 'Yakunlangan'),
    ]

    customer = models.ForeignKey(CustomerDelivery, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"


class TakeoutItem(models.Model):
    order = models.ForeignKey(Takeout, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"


class DeliveryItem(models.Model):
    order = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"