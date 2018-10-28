from django.db import models
from account.models import User
# Create your models here.


class PermissionGroup(models.Model):
    GID = models.AutoField(primary_key=True, unique=True)
    group_name = models.CharField(max_length=20)


class User_Permission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    permission = models.CharField(max_length=200)
