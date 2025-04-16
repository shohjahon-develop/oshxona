from django.db import models
from menu.models import MenuItem
from users.models import Customer, CustomerDelivery, User


class Table(models.Model):
    PLACE_CHOICE = [
        ('hall', 'Zall'),
        ('second floor', 'Ikkinchi qavat'),
        ('basement', 'Padval'),
    ]
    place = models.CharField(max_length=20, choices=PLACE_CHOICE, default='hall')
    number = models.PositiveIntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.number}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutish jarayonida'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('served', 'Yakunlangan'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    def calculate_total_price(self):
        if self.items.exists():
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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Takeout {self.id} - {self.status}"

    def calculate_total_price(self):
        if self.items.exists():
            self.total_price = sum(item.quantity * item.menu_item.price for item in self.items.all())
            self.save()


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutish jarayonida'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        # YANGI STATUS:
        ('delivering', 'Yetkazilmoqda'),  # 'delivering' kabi inglizcha kalit so'z ishlatish yaxshiroq
        # O'ZGARTIRILGAN TARJIMA:
        ('served', 'Yetkazildi'),
    ]
    customer = models.ForeignKey(CustomerDelivery, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # --- assigned_to maydoni olib tashlandi ---
    # assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
    #                                 related_name='assigned_deliveries', limit_choices_to={'role': 'delivery'})

    def __str__(self):
        return f"Delivery {self.id} - {self.status}"

    def calculate_total_price(self):
        # Bu metod to'g'ri ishlashi uchun items bog'liqligi kerak
        # Agar items yaratilgandan keyin hisoblanayotgan bo'lsa, joyida
        total = sum(item.quantity * item.menu_item.price for item in self.items.all()) if self.items.exists() else 0.00
        self.total_price = total
        # save() ni create/update logikasida qilish yaxshiroq
        # self.save() # Yoki shu yerda qolsin


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class TakeoutItem(models.Model):
    takeout = models.ForeignKey(Takeout, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class DeliveryItem(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"