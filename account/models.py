from django.db import models

# Create your models here.


class QuestionList(models.Model):
    question = models.CharField(max_length=50, verbose_name="Question")


class User(models.Model):
    uid = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=20, default="None", verbose_name="Username")
    password = models.CharField(max_length=16, verbose_name='password')
    email = models.EmailField(verbose_name='Email')
    question = models.ForeignKey(QuestionList, on_delete=models.CASCADE)
    answer = models.CharField(max_length=50, verbose_name="Question")
    head_picture_adress = models.CharField(max_length=200, default="")
    permission_group = models.IntegerField(default=0, verbose_name="Permission Group")
    sign_up_time = models.TimeField(auto_now=True)
    last_login_time = models.TimeField(auto_now_add=True)
    sign_up_ip = models.GenericIPAddressField()
    last_login_ip = models.GenericIPAddressField()




