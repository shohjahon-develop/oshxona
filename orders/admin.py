from django.contrib import admin
from .models import Table, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'table', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]

admin.site.register(Table)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
