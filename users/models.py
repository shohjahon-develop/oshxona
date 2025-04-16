from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom User Manager (Foydalanuvchilarni qo‘shish uchun)
class UserManager(BaseUserManager):
    def create_user(self, phone, name, password=None, role=None):
        if not phone:
            raise ValueError("Telefon raqami majburiy")
        user = self.model(phone=phone, name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password):
        user = self.create_user(phone, name, password, role="admin")
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

# Custom User modeli
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('waiter', 'Afitsant'),
        ('chef', 'Oshpaz'),
        ('cashier', 'Kassir'),
        ('delivery', 'Yetkazib beruvchi'),
        ('admin', 'Admin'),
    ]

    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    pin_code = models.CharField(max_length=4, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Admin panelga kirish huquqi

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.role})"


class CustomerDelivery(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.phone})"




class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Setting(models.Model):
    restaurant_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    service_charge = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    description = models.TextField(default="Milliy va zamonaviy taomlar restorani")
    currency = models.CharField(max_length=3, default="So'm (UZS)")
    language = models.CharField(max_length=2, default="O'zbek")

    def __str__(self):
        return self.restaurant_name