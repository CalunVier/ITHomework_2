from django.shortcuts import render, redirect, reverse
from .renders import ArticleListRender, ArticleRender, login_status, CommentsListRender
from .models import ArticlesList, CommentList, ArticleGroups
from account.models import User, UserFavoriteArticles
from .forms import NewArticleForm
from django.http.response import Http404
from permission.permission import Permission, user_permission_add
import re
import datetime


def index(request):
    return render(request, 'index.html', {'status': login_status(request)})


def permission_dead(request):
    return render(request, "Permission_Refused.html")


# 文章列表，一般作iframe
def article_list(request, source, page):
    print("blog.views.article_list():source:", source)
    print("blog.views.article_list():page:", page)
    if not page:
        page = 1
    else:
        try:
            page = int(page)
        except ValueError:
            page = 1
    if request.method == 'GET':
        return ArticleListRender(request, source).init_dictionary(page).rendering()


# 新文章
def new_article(request):
    if Permission(request).check_login().result():
        user = User.objects.get(uid=int(request.COOKIES.get('UID')))
        if request.method == 'GET':
            return render(request, "new_article.html", {'new_article_form': NewArticleForm()})
        if request.method == 'POST':
            form = NewArticleForm(request.POST)     # 获取列表
            if form.is_valid():
                print(form.cleaned_data['title'])
                print(form.cleaned_data['content'])     # debug部分
                group = form.cleaned_data['group']
                if not group:       # 判断是否填写group，若未填写，则默认default
                    group = 'Default'
                    if not ArticleGroups.objects.filter(owner=user, group_name=group):      # 检查组是否存在
                        ArticleGroups(group_name=group, owner=user).save()
                # 将文章写入数据库
                the_new_article = ArticlesList(article_name=form.cleaned_data['title'],
                                               content=form.cleaned_data['content'],
                                               author=user,
                                               Visibility=form.cleaned_data["visibility"])
                the_new_article.save()

                # 写入可见权限
                can_see_users = re.split(r"[\s,]+", form.cleaned_data['who_can_see'])
                for u in can_see_users:
                    try:
                        can_see_user = User.objects.get(username=u)
                        user_permission_add(can_see_user, 'blog.{0}.view'.format(the_new_article.aid))
                    except User.DoesNotExist:
                        continue

                # 写入可修改权限
                can_edit_users = re.split(r"[\s,]+", form.cleaned_data['who_can_edit'])
                for u in can_edit_users:
                    try:
                        can_edit_user = User.objects.get(username=u)
                        user_permission_add(can_edit_user, 'blog.{0}.edit'.format(the_new_article.aid))
                    except User.DoesNotExist:
                        continue

                return redirect(reverse("account:UserHome"))
            return render(request, "new_article.html", {'new_article_form': form, 'message': '提交失败'})
    else:
        return render(request, "Permission_Refused.html")


# 文章页面
def article(request, aid):
    if request.method == 'GET':
        try:    # 获取文章aid
            aid = int(aid)
            art = ArticlesList.objects.get(aid=aid)
        except BaseException:   # 找不到就404
            return Http404()
        # 检查Visible权限和view权限

        if Permission(request, logged=True).check_permission_blog(art, 'view').result():
            print("blog.views.article():aid:", aid)
            return ArticleRender(request, aid, {'aid': aid, 'logged': Permission(request).check_login().logged}).rendering()      # 渲染
        else:
            return render(request, "Permission_Refused.html")
    return Http404()        # 找不到就404


def comments(request, aid, page):
    print("article_list:", page)
    if not page:
        page = 1
    else:
        try:
            page = int(page)
        except ValueError:
            page = 1
    print("blog.views.comments():", page)
    if request.method == 'GET':
        print('blog.views.comments():GET')
        return CommentsListRender(request).init_dictionary(ArticlesList.objects.get(aid=aid), page).rendering()
    if request.method == 'POST':
        print('blog.views.comments():POST')
        art = None
        try:        # 尝试获取article model对象
            art = ArticlesList.objects.get(aid=aid)
        except ArticlesList.DoesNotExist:
            pass
        if Permission(request).check_login().check_permission_blog(art, 'comment').result():    # 权限检查
            print("blog.views.comments():POST:comment权限检查通过")
            content = request.POST.get('comment_content')       # 获取评论内容
            print("blog.views.comments():POST:content:", content)
            if (not content) or len(content) > 250:     # 检查评论内容是否合法
                if Permission(request, logged=True).check_permission_blog(art, 'view').result():
                    print("blog.views.article():aid:", aid)
                    return ArticleRender(request, aid, {'aid': aid, 'comment_submit_message': "评论提交失败"}).rendering()  # 渲染
                else:
                    return render(request, "Permission_Refused.html")
            print("blog.views.comments():POST:评论内容合法")
            print("blog.views.comments():POST:开始写入数据库")
            CommentList(article=art,
                        content=content,
                        author=User.objects.get(uid=int(request.COOKIES.get("UID")))).save()
        else:
            return render(request, "Permission_Refused.html")
        return redirect('/blog/article/{0}'.format(art.aid))


def delete_article(request):
    if request.method == "GET":
        aid = int(re.match(r'.+blog/article/(\d+)', request.META['HTTP_REFERER']).group(1))
        art = ArticlesList.objects.filter(aid=aid)
        if Permission(request).check_permission_blog(art[0], r'edit.delete'):
            art.delete()
            return redirect(reverse("account:UserHome"))
        else:
            return render(request, "Permission_Refused.html")


def like_article(request, aid):
    if request.method == 'GET':
        if Permission(request).check_login().result():
            try:
                aid = int(aid)
                art = ArticlesList.objects.get(aid=aid)
            except BaseException:
                return permission_dead(request)
            user = User.objects.get(uid=request.COOKIES.get('UID'))
            if not UserFavoriteArticles.objects.filter(user=user, article=art):     # 查重
                UserFavoriteArticles(user=user, article=art).save()
        return redirect('/blog/article/{0}'.format(aid))


def edit_article(request, aid):
    try:
        art = ArticlesList.objects.get(aid=int(aid))
    except BaseException:
        return Http404
    if Permission(request).check_login().check_permission_blog(art, 'edit'):
        user = User.objects.get(uid=request.COOKIES.get('UID'))
        if not art.group:
            art.group = ArticleGroups.objects.get(owner=user, group_name='Default')
        if request.method == 'GET':
            return render(request, "edit_article.html", {'title': art.article_name,
                                                         'content': art.content,
                                                         'Visibility': art.Visibility,
                                                         'group': art.group.group_name,
                                                         # 'who_can_see': art.whocansee,
                                                         # 'who_can_edit': art.whocanedit,
                                                         # 'who_can_not_see': art.whocannotsee,
                                                         'aid': aid
                                                         })
        if request.method == 'POST':
            if request.POST.get('title') and art.article_name != request.POST.get('title'):
                art.article_name = request.POST.get('title')
            if request.POST.get('content') and art.content != request.POST.get('content'):
                art.content = request.POST.get('content')
            if art.Visibility != request.POST.get('visibility'):
                art.Visibility = request.POST.get('visibility')

            group = request.POST.get('group')
            if not group:  # 判断是否填写group，若未填写，则默认default
                group = 'Default'
                if not ArticleGroups.objects.filter(owner=user, group_name=group):  # 检查组是否存在
                    ArticleGroups(group_name=group, owner=user).save()
            if art.group != ArticleGroups.objects.get(owner=user, group_name=group):
                art.group = ArticleGroups.objects.get(owner=user, group_name=group)
            art.last_modified = datetime.datetime.now()
            art.save()
        return redirect('/blog/article/{0}'.format(aid))
    else:
        return permission_dead(request)
