# Generated by Django 5.1.4 on 2025-03-06 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_order_is_paid_order_status_and_more'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PaymentStatus',
            new_name='Payment',
        ),
    ]
