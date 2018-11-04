from django.shortcuts import render, redirect, reverse
from .renders import article_list_render
from .models import ArticlesList
from account.models import User
from .forms import NewArticleForm
from django.http.response import Http404


def index(request):
    return render(request, 'index.html')


# 文章列表，一般作iframe
def article_list(request, source):
    if request.method == 'GET':
        if source == 'HomePage':
            article_list_db = ArticlesList.objects.all()
            article_list_db.reverse()
            article_list_db = article_list_db[:10]
            articles = []
            for article in article_list_db:
                articles.append({'name': article.article_name, 'aid': article.aid})
            return article_list_render(request, articles)


# 新文章
def new_article(request):
    user = User.objects.get(uid=int(request.COOKIES.get('UID')))

    if request.method == 'GET':
        return render(request, "new_article.html", {'new_article_form': NewArticleForm()})
    if request.method == 'POST':
        form = NewArticleForm(request.POST)
        if form.is_valid():
            ArticlesList(article_name=form.cleaned_data['title'], content=form.cleaned_data['content'], author=user).save()
            return redirect(reverse("account:UserHome"))
        return render(request, "new_article.html", {'new_article_form': form, 'message': '提交失败'})


# 文章页面
def article(request,aid):
    if request.method == 'GET':
        try:
            aid = int(aid)
        except TypeError:
            return Http404()
        art = ArticlesList.objects.filter(aid=aid)
        if art:
            return render(request, "article.html", {'title':art[0].article_name, 'content':art[0].content})
    return Http404()