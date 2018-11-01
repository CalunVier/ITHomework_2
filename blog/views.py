from django.shortcuts import render
from .renders import article_list_render
from .models import ArticlesList



def index(requset):
    return render(requset, 'index.html')


def article_list(request, source):
    if request.method == 'GET':
        if source == 'HomePage':
            article_list_db = ArticlesList.objects.all()
            article_list_db.reverse()
            article_list_db = article_list_db[:10]
            articles = []
            for article in article_list_db:
                articles.append({'name': article.article_name, 'address': "blog/articles/blog_"+str(article.aid)})
            return article_list_render(request, articles)
