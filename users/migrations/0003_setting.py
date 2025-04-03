# Generated by Django 5.1.7 on 2025-04-03 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customerdelivery'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.CharField(max_length=200)),
                ('description', models.TextField(default='Milliy va zamonaviy taomlar restorani')),
                ('currency', models.CharField(default="So'm (UZS)", max_length=3)),
                ('language', models.CharField(default="O'zbek", max_length=2)),
            ],
        ),
    ]
