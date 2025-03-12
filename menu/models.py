from django.db import models

# Create your models here.
class MenuItem(models.Model):
    CATEGORY_CHOICES = (
        ('food', 'Ovqat'),
        ('drink', 'Ichimlik'),
        ('fastfood', 'Fast Food'),
        ('dessert', 'Shirinlik'),
        ('hot food','Issiq Taomlar'),
        ('salat','Salatlar')
    )
    img = models.ImageField(upload_to='images/')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
