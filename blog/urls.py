"""ITHomework_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^articlelist/([^/]+)(?:/(\d*))?', views.article_list, name='ArticleList'),
    url(r'^new_article/', views.new_article, name='NewArticle'),
    url(r'^article/(.+)', views.article, name="Article"),
    url(r'^comment/([^/]+)(?:/(\d*))?', views.comments, name='CommentsList'),
    url(r'^delete/$', views.delete_article, name="Delete"),
    url(r'^like/(\d+)', views.like_article, name="LikeArticle"),
    url(r'^editarticle/(.+)', views.edit_article, name="EditArticle")
]
