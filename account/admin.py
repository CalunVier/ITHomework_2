from django.contrib import admin
from .models import *

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('uid',
                    'username',
                    'password',
                    'email',
                    'question',
                    'answer',
                    'sign_up_time',
                    'sign_up_ip',
                    'last_login_time',
                    'last_login_ip'
                    )
admin.site.register(User, UserAdmin)


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('uid', 'sex', 'phone_number', 'profile')


admin.site.register(UserInfo, UserInfoAdmin)


class UserFavoriteArticlesAdmin(admin.ModelAdmin):
    list_display = ('user', 'article')


admin.site.register(UserFavoriteArticles, UserFavoriteArticlesAdmin)


admin.site.register(QuestionList)
