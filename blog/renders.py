from django.shortcuts import render
from .models import ArticlesList
from account.models import User
from django.http.response import Http404
import markdown


# def article_list_render(request, articles):
#     c = {'articles': articles}
#     return render(request, "article_list.html", c)


class Render(object):
    def __init__(self,request,html,dic=None):
        self.request = request
        self.template = html
        self.dictionary = dic

    def rendering(self):
        return render(self.request, self.template, self.dictionary)


class ArticleListRender(Render):
    def __init__(self, request, source, dic={}):
        super().__init__(request, "article_list.html", dic)  # 设置article_list.html，同时初始化dictionary
        self.source = source

    def item_getter(self, dbq, page, number=10):
        len_dbq = len(dbq)
        if (len_dbq-page*number-1) < 0:
            return dbq[::-1]
        else:
            return dbq[len_dbq-(page-1)*number-1:len_dbq-page*number-1:-1]

    def init_dictionary(self, page=1):
        # Index源，构建的文章列表
        if self.source == 'Index':
            article_list_db = self.item_getter(ArticlesList.objects.exclude(Visibility=1).exclude(Visibility=2), page)
            articles = []
            for article in article_list_db:
                articles.append({'name': article.article_name, 'aid': article.aid})
            self.dictionary['articles'] = articles

        # UserHome源，构建文章列表
        if self.source == 'UserHome':
            user = User.objects.get(uid=int(self.request.COOKIES.get('UID')))
            article_list_db = self.item_getter(ArticlesList.objects.filter(author=user), page)
            articles = []
            for article in article_list_db:
                articles.append({'name': article.article_name, 'aid': article.aid})
            self.dictionary['articles'] = articles

        return self


class ArticleRender(Render):
    def __init__(self, request, aid, dic={}):
        super().__init__(request, 'article.html', dic)
        # try:
        art = ArticlesList.objects.get(aid=aid)
        dic['title'] = art.article_name
        dic['author'] = art.author.username
        dic['issuing_time'] = art.issuing_time.isoformat()
        dic['last_modified'] = art.last_modified.isoformat()
        dic['content'] = markdown.markdown(art.content)
        print(dic['content'])
        self.dictionary = dic
        # except BaseException:
        #     self.rendering = lambda: Http404()


# class CommentsRender(object):
#
#     def __init__(self):
#


def login_status(request):
    UNLOGIN = "<a href=\"account\\register\" style=\"float: right;font-size: 12px\">注册</a>" \
                "<a href=\"account\\login\" style=\"float: right;font-size: 12px;padding-right: 3px\">登陆</a>"
    try:
        uid = request.COOKIE.get('UID')
    except AttributeError:
        return
    if uid == '':
        return "<a href=\"{% url 'account:Register' %}\" style=\"float: right;font-size: 12px\">注册</a>" \
               "<a href=\"{% url 'account:Login' %}\" style=\"float: right;font-size: 12px;padding-right: 3px\">登陆</a>"
    return True
