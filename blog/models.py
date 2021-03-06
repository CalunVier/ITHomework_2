from django.db import models
from account.models import User

# Create your models here.


class ArticleGroups(models.Model):
    group_name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Visibility = models.IntegerField(choices=((0, 'Public'), (1, 'Protected'), (2, 'Private')), default=0)

    def __str__(self):
        return self.owner.username+'.'+self.group_name


class ArticlesList(models.Model):
    aid = models.AutoField(primary_key=True, unique=True)
    article_name = models.CharField(max_length=60)
    content = models.TextField(max_length=500000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ArticleGroups, null=True, on_delete=models.CASCADE)
    issuing_time = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    Visibility = models.IntegerField(default=0, choices=((0, 'Public'), (1, 'Protected'), (2, 'Private')))
    whocansee = models.CharField(null=True, max_length=100, verbose_name='Who Can See')
    whocannotsee = models.CharField(null=True, max_length=100, verbose_name='Who Can Not See')
    whocanedit = models.CharField(null=True, max_length=100, verbose_name='Who Can Edit')

    def __str__(self):
        return self.aid


class CommentList(models.Model):
    article = models.ForeignKey(ArticlesList, on_delete=models.CASCADE)
    content = models.CharField(max_length=250)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    superior = models.ForeignKey(to='self', null=True)

    def __str__(self):
        return self.content
