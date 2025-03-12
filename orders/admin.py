from django.contrib import admin
from .models import *

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class TakeoutItemInline(admin.TabularInline):
    model = TakeoutItem
    extra = 1

class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]


class TakeoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer',  'status', 'created_at')
    list_filter = ('status',)
    inlines = [TakeoutItemInline]

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [DeliveryItemInline]

admin.site.register(Table)
admin.site.register(Order, OrderAdmin)
admin.site.register(Takeout,TakeoutAdmin)
admin.site.register(Delivery,DeliveryAdmin)
admin.site.register(OrderItem)
admin.site.register(TakeoutItem)
admin.site.register(DeliveryItem)
