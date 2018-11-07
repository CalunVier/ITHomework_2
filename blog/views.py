from django.shortcuts import render, redirect, reverse
from .renders import ArticleListRender, ArticleRender, login_status
from .models import ArticlesList
from account.models import User
from .forms import NewArticleForm
from django.http.response import Http404
import re



def index(request):
    return render(request, 'index.html', {'status': login_status(request)})


# 文章列表，一般作iframe
def article_list(request, source):
    if request.method == 'GET':
        return ArticleListRender(request, source).init_dictionary().rendering()


# 新文章
def new_article(request):
    user = User.objects.get(uid=int(request.COOKIES.get('UID')))

    if request.method == 'GET':
        return render(request, "new_article.html", {'new_article_form': NewArticleForm()})
    if request.method == 'POST':
        form = NewArticleForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['title'])
            print(form.cleaned_data['content'])
            ArticlesList(article_name=form.cleaned_data['title'], content=form.cleaned_data['content'], author=user).save()
            return redirect(reverse("account:UserHome"))
        return render(request, "new_article.html", {'new_article_form': form, 'message': '提交失败'})


# 文章页面
def article(request, aid):
    if request.method == 'GET':
        try:
            aid = int(aid)
        except TypeError:
            return Http404()
        # art = ArticlesList.objects.filter(aid=aid)
        # if art:
        return ArticleRender(request, aid).rendering()
    return Http404()


def comments(request,aid):
    if request.method == 'GET':

        return render(request, "comments.html")


def delete_article(request):
    if request.method == "GET":
        aid = int(re.match(r'.+blog/article/(\d+)', request.META['HTTP_REFERER']).group(1))
        ArticlesList.objects.filter(aid=aid).delete()
        return redirect(reverse("account:UserHome"))
