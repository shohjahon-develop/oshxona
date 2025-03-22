from django.db import models
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

    def calculate_total_price(self):
        total = sum(item.menu_item.price * item.quantity for item in self.items.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.status} - Total: {self.total_price} so‘m"

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
        total = sum(item.menu_item.price * item.quantity for item in self.items.all())
        self.total_price = total
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
        total = sum(item.menu_item.price * item.quantity for item in self.items.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Delivery {self.id} - {self.status} - Total: {self.total_price} so‘m"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.calculate_total_price()  # ✅ Buyurtma umumiy narxini yangilash

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class TakeoutItem(models.Model):
    order = models.ForeignKey(Takeout, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.calculate_total_price()  # ✅ Takeout umumiy narxini yangilash

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class DeliveryItem(models.Model):
    order = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.calculate_total_price()  # ✅ Delivery umumiy narxini yangilash

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
