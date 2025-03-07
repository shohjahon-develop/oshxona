from django.contrib import admin

from roles.models import *

admin.site.register(Role)
admin.site.register(RolePermission)
admin.site.register(Permission)