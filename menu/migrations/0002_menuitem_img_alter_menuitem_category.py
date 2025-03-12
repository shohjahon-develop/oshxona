# Generated by Django 5.1.7 on 2025-03-12 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='img',
            field=models.ImageField(default=1, upload_to='images/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='category',
            field=models.CharField(choices=[('food', 'Ovqat'), ('drink', 'Ichimlik'), ('fastfood', 'Fast Food'), ('dessert', 'Shirinlik'), ('hot food', 'Issiq Taomlar'), ('salat', 'Salatlar')], max_length=20),
        ),
    ]
