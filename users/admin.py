from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import User, Customer


# Admin panelda parol qo'shish uchun forma
class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone', 'name', 'password', 'role')


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = UserCreationForm
    list_display = ('name', 'phone', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    ordering = ('name',)

    fieldsets = (
        (None, {'fields': ('phone', 'name', 'password', 'role', 'is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'password', 'role')}
         ),
    )

    search_fields = ('name', 'phone')
    filter_horizontal = ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer)