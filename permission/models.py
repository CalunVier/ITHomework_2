from django.db import models
from account.models import User
# Create your models here.


# 权限组列表
class PermissionGroup(models.Model):
    gid = models.AutoField(primary_key=True, unique=True, verbose_name="GID")
    group_name = models.CharField(max_length=20, verbose_name="Permission Group Name")


# 用户权限表
class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Permission's Owner")
    permission = models.CharField(max_length=200, verbose_name="Permission")
