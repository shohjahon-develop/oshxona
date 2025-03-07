from django.contrib import admin
from .models import Payment

class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'updated_at')
    list_filter = ('status',)

admin.site.register(Payment, PaymentStatusAdmin)
