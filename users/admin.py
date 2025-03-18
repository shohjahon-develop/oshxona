from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import User, Customer, CustomerDelivery


# Admin panelda parol qo'shish uchun forma
class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone', 'name', 'password', 'role','pin_code')


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = UserCreationForm
    list_display = ('name', 'phone', 'role','pin_code' ,'is_active')
    list_filter = ('role', 'is_active')
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('phone', 'name', 'password', 'role','pin_code', 'is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'password', 'role','pin_code')}
         ),
    )

    search_fields = ('name', 'phone')
    filter_horizontal = ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer)
admin.site.register(CustomerDelivery)


# admin number = 930034867
# admin password = 20062006