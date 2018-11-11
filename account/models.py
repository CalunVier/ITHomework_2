from django.db import models
import datetime

# Create your models here.


# 密保问题列表
class QuestionList(models.Model):
    question = models.CharField(max_length=50, verbose_name="Question")

    def __str__(self):
        return self.question

# 用户注册登陆安全信息
class User(models.Model):
    uid = models.AutoField(primary_key=True, unique=True, verbose_name='UID')
    username = models.CharField(max_length=20, default="None", verbose_name="Username")
    password = models.CharField(max_length=16, verbose_name='Password')
    email = models.EmailField(verbose_name='Email')
    question = models.ForeignKey(QuestionList, on_delete=models.CASCADE, verbose_name='Safe Question')
    answer = models.CharField(max_length=50, verbose_name="Safe Answer")
    permission_group = models.ForeignKey('permission.PermissionGroup', models.CASCADE, null=True, verbose_name="Permission Group")
    sign_up_time = models.DateTimeField(auto_now=True, verbose_name="Sign Up Time")
    last_login_time = models.DateTimeField(auto_now_add=True, verbose_name="Last Login Time")
    sign_up_ip = models.GenericIPAddressField(verbose_name="Sign Up IP")
    last_login_ip = models.GenericIPAddressField(verbose_name="Last Login IP")

    def __str__(self):
        return self.username


# 用户信息
class UserInfo(models.Model):
    uid = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, verbose_name="UID")
    sex = models.IntegerField(choices=((1, 'man'), (2, 'female')), null=True, verbose_name="Sex")
    phone_number = models.IntegerField(null=True, verbose_name="Phone Number")
    profile = models.CharField(max_length=150, null=True, verbose_name="Profile")

    def __str__(self):
        return self.uid.username+"'s info"


# Session
class LoginSession(models.Model):
    uid = models.IntegerField()
    login_key = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)


class UserFavoriteArticles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    article = models.ForeignKey('blog.ArticlesList', on_delete=models.CASCADE, verbose_name='Article')

    def __str__(self):
        return self.user.username+"'s FavoriteArticles"
