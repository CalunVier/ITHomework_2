from django.contrib import admin
from .models import *
# Register your models here.


class ArticleListAdmin(admin.ModelAdmin):
    list_display = ('aid', 'article_name', 'author', 'group', 'issuing_time', 'last_modified', 'Visibility')


admin.site.register(ArticlesList, ArticleListAdmin)

admin.site.register(ArticleGroups)


class CommentsListAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'author', 'time', 'content')


admin.site.register(CommentList, CommentsListAdmin)

