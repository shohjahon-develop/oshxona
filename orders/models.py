from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from users.models import Customer, CustomerDelivery
from menu.models import MenuItem

class Table(models.Model):
    PLACE_CHOICE = [
        ('hall', 'Zall'),
        ('second floor', 'Ikkinchi qavat'),
        ('basement', 'Padval'),
    ]
    place = models.CharField(max_length=20, choices=PLACE_CHOICE, default='hall')
    number = models.PositiveIntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)  # Stol band yoki yo‘qligi

    def __str__(self):
        return f"Table {self.number}"

class Order(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    STATUS_CHOICES = [
        ('pending', 'Kutish jarayonida'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('served', 'Yakunlangan'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Umumiy narx

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    def calculate_total_price(self):
        if self.items.exists():  # ✅ Agar items bo‘lsa, hisoblash
            self.total_price = sum(item.quantity * item.menu_item.price for item in self.items.all())
            self.save()

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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Umumiy narx

    def calculate_total_price(self):
        if self.items.exists():  # ✅ Agar items bo‘lsa, hisoblash
            self.total_price = sum(item.quantity * item.menu_item.price for item in self.items.all())
            self.save()

    def __str__(self):
        return f"Takeout {self.id} - {self.status} - Total: {self.total_price} so‘m"

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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Umumiy narx

    def calculate_total_price(self):
        if self.items.exists():  # ✅ Agar items bo‘lsa, hisoblash
            self.total_price = sum(item.quantity * item.menu_item.price for item in self.items.all())
            self.save()

    def __str__(self):
        return f"Delivery {self.id} - {self.status} - Total: {self.total_price} so‘m"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):  # ✅ Saqlanganda umumiy narxni hisoblaydi
        super().save(*args, **kwargs)
        self.order.calculate_total_price()  # ✅ Buyurtma umumiy narxini yangilash

    def delete(self, *args, **kwargs):  # ✅ O‘chirilganda umumiy narxni yangilash
        super().delete(*args, **kwargs)
        self.order.calculate_total_price()


    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class TakeoutItem(models.Model):
    order = models.ForeignKey(Takeout, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.calculate_total_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.calculate_total_price()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class DeliveryItem(models.Model):
    order = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.calculate_total_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.calculate_total_price()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"



@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    instance.order.calculate_total_price()

@receiver(post_save, sender=TakeoutItem)
@receiver(post_delete, sender=TakeoutItem)
def update_takeout_total(sender, instance, **kwargs):
    instance.order.calculate_total_price()

@receiver(post_save, sender=DeliveryItem)
@receiver(post_delete, sender=DeliveryItem)
def update_delivery_total(sender, instance, **kwargs):
    instance.order.calculate_total_price()