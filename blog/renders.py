from django.shortcuts import render
from .models import ArticlesList
from account.models import User
from django.http.response import Http404


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
    def __init__(self, request, source, page=1, dic={}):
        super().__init__(request,"article_list.html",dic)  # 设置article_list.html，同时初始化dictionary
        page = (page - 1)*10
        # Index源,构建文章列表
        if source == 'Index':
            article_list_db = ArticlesList.objects.all()
            article_list_db.reverse()
            article_list_db = article_list_db[page:page+10]
            articles = []
            for article in article_list_db:
                articles.append({'name': article.article_name, 'aid': article.aid})
            self.dictionary['articles'] = articles
        # UserHome源，构建文章列表
        if source == 'UserHome':
            user = User.objects.get(uid=int(request.COOKIES.get('UID')))
            article_list_db = ArticlesList.objects.filter(author=user)
            article_list_db.reverse()
            article_list_db = article_list_db[page:page+10]
            articles = []
            for article in article_list_db:
                articles.append({'name': article.article_name, 'aid': article.aid})
            self.dictionary['articles'] = articles


class ArticleRender(Render):
    def __init__(self, request, aid, dic={}):
        super().__init__(request, 'article.html', dic)
        # try:
        art = ArticlesList.objects.get(aid=aid)
        dic['title'] = art.article_name
        dic['author'] = art.author.username
        dic['issuing_time'] = art.issuing_time.isoformat()
        dic['last_modified'] = art.last_modified.isoformat()
        dic['content'] = art.content
        self.dictionary = dic
        # except BaseException:
        #     self.rendering = lambda: Http404()


# class CommentsRender(object):
#
#     def __init__(self):
#
