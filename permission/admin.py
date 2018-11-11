from django.contrib import admin
from .models import *
# Register your models here.


class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'permission', 'rule')


admin.site.register(UserPermission, UserPermissionAdmin)
