from django.db import models
from account.models import User

# Create your models here.


class ArticleGroups(models.Model):
    group_name = models.CharField(max_length=50)
    prossessor = models.ForeignKey(User, on_delete=models.CASCADE)
    Visibility = models.IntegerField(choices=((0, 'Public'), (1, 'Protected'), (2, 'Private')))


class ArticlesList(models.Model):
    aid = models.AutoField(primary_key=True, unique=True)
    article_name = models.CharField(max_length=60)
    article_address = models.CharField(max_length=200)
    auther = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ArticleGroups, on_delete=models.CASCADE)
    issuing_time = models.TimeField(auto_now=True)
    last_modified = models.TimeField(auto_now_add=True)
    permissions = models.CharField(default="", max_length=1000, verbose_name="Permissions")
    Visibility = models.IntegerField(choices=((0, 'Public'), (1, 'Protected'), (2, 'Private')))


class CommentList(models.Model):
    auther = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.TimeField(auto_now=True)
    superior = models.ForeignKey(to='self')