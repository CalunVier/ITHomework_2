from django.shortcuts import render
from .models import ArticlesList, CommentList, ArticleGroups
from account.models import User, UserFavoriteArticles
import re, markdown
from permission.permission import Permission


# 渲染器基类
class Render(object):
    def __init__(self, request, html, dic=None):
        self.request = request
        self.template = html
        self.dictionary = dic

    def rendering(self):
        print(self.dictionary)
        return render(self.request, self.template, self.dictionary)


# 文章列表渲染器
class ArticleListRender(Render):
    def __init__(self, request, source, dic=None):
        if not dic:
            dic = {}
        super().__init__(request, "article_list.html", dic)  # 设置article_list.html，同时初始化dictionary
        self.source = source

    # 文章列表切片器   我是谁？我在哪？我写的是啥？
    @staticmethod
    def item_slice(dbq, page, number):
        print("ArticleListRender.item_slice():page:", page)
        len_dbq = len(dbq)
        if not len_dbq:
            return dbq
        elif (len_dbq-page*number-1) < 0:
            return dbq[len_dbq-(page-1)*number-1::-1]
        else:
            return dbq[len_dbq-(page-1)*number-1:len_dbq-page*number-1:-1]

    # 文章列表内容获取器
    def item_getter(self, article_list_db, page, number):
        print("ArticleListRender.item_getter():page:", page)
        article_sum = len(article_list_db)  # 获取可显示文章总数
        pages = article_sum // number  # 获取页面数
        if len(article_list_db) % number:  # 如果有余数，pages+=1，因为//会向下取整
            pages += 1
        article_list_db = self.item_slice(article_list_db, page, number)  # 切取单页articles
        # articles列表格式化
        articles = []
        for article in article_list_db:
            articles.append({'name': article.article_name, 'aid': article.aid})
        self.dictionary['articles'] = articles              # 文章列表写入字典
        self.dictionary['pages'] = range(1, pages + 1)      # 将总页面写入字典
        self.dictionary['page'] = page                      # 将当前页面的值写入字典
        self.dictionary['source'] = self.source             # 将请求来源写入字典

    # 字典初始化
    def init_dictionary(self, page=1, number=10):
        # Index源，构建的文章列表
        print("ArticleListRender.init_dictionary():page:", page)
        if self.source == 'Index':
            article_list_db = ArticlesList.objects.exclude(Visibility=1).exclude(Visibility=2)  # 获取所有可显示的文章
            self.item_getter(article_list_db, page, 20)

        # UserHome源，构建文章列表
        home_source = re.match('^UserHome_(.+)', self.source)
        print("ArticleListRender.init_dictionary():self.source:", self.source)
        if home_source:
            print("ArticleListRender.init_dictionary():UserHome源", home_source.group(1))
            user = User.objects.get(uid=int(self.request.COOKIES.get('UID')))
            article_list_db = ArticlesList.objects.filter(author=user)
            if int(home_source.group(1)):
                group = ArticleGroups.objects.get(id=int(home_source.group(1)))
                article_list_db = article_list_db.filter(group=group)
            self.item_getter(article_list_db, page, number)

        if self.source == 'Favourite':
            user = User.objects.get(uid=int(self.request.COOKIES.get('UID')))
            article_list_db_row = UserFavoriteArticles.objects.filter(user=user)
            article_list_db = []
            for art in article_list_db_row:
                article_list_db.append(art.article)
            self.item_getter(article_list_db, page, number)

        return self


class ListRender(Render):
    def __init__(self, request, template, dic):
        super().__init__(request, template, dic)

    # 文章列表切片器   我是谁？我在哪？我写的是啥？
    @staticmethod
    def item_slice(dbq, page, number):
        len_dbq = len(dbq)
        print(len_dbq, page, number)
        if not len_dbq:
            return dbq
        elif (len_dbq - page * number - 1) < 0:
            return dbq[len_dbq - (page - 1) * number - 1::-1]
        else:
            return dbq[len_dbq - (page - 1) * number - 1:len_dbq - page * number - 1:-1]

        # 列表内容获取器
    def item_getter(self, list_db, page, number):
        items_queryset = self.item_slice(list_db, page, number)  # 切取单页items
        self.dictionary['pages'] = range(1, self.pages_getter(list_db, number)+1)   # 在切取本页items时同时初始化pages
        return items_queryset

    def pages_getter(self, list_db, number):
        item_sum = len(list_db)  # 获取可显示文章总数
        pages = item_sum // number  # 获取页面数
        if len(list_db) % number:  # 如果有余数，pages+=1，因为//会向下取整
            pages += 1
        return pages


class CommentsListRender(ListRender):
    def __init__(self, request, dic=None):
        if not dic:
            dic = {}
        super().__init__(request, 'comments.html', dic)

    # 获取评论
    def comments_getter(self, article, page, number):
        comments_db = CommentList.objects.filter(article=article)      # 获取本文章的所有评论
        comment_queryset = self.item_getter(comments_db, page, number)      # 获取本页评论的QuerySet
        return comment_queryset

    # 初始化字典
    def init_dictionary(self, article, page=1, number=10,):
        print("CommentsListRender.init_dictionary():page:", page)
        comment_queryset = self.comments_getter(article, page, number)   # 写入comments的QuerySet
        comments = []       # comments列表，存放comment字典
        for comment in comment_queryset:
            superior = None
            if comment.superior:
                try:
                    superior_comment = CommentList.objects.get(id=comment.superior.id)
                    superior = {'author': superior_comment.author.username, 'content': superior_comment.content}
                except CommentList.DoesNotExist:
                    pass
            comments.append({'content': comment.content,            # 写入comment
                             'author': comment.author.username,
                             'issue_time': comment.time,
                             'superior': superior})
        self.dictionary['comments'] = comments
        self.dictionary['page'] = page      # 写入page
        self.dictionary['aid'] = article.aid

        return self


# 文章页面渲染器
class ArticleRender(Render):
    def __init__(self, request, aid, dic=None):
        if not dic:
            print("ArticleRender.__init__():字典值为：", dic, "初始化字典")
            dic = {}
        super().__init__(request, 'article.html', dic)
        # try:
        print("ArticleRender.__init__():字典数据写入前", dic)
        art = ArticlesList.objects.get(aid=aid)
        dic['title'] = art.article_name
        dic['author'] = art.author.username
        dic['issuing_time'] = art.issuing_time.isoformat()
        dic['last_modified'] = art.last_modified.isoformat()
        dic['content'] = art.content
        print(dic['content'])
        dic['login_status'] = login_status(request)
        dic['edit_permission'] = Permission(request).check_login().check_permission_blog(art, do='edit').result()
        if dic['edit_permission']:
            dic['delete_permission'] = True
        else:
            dic['delete_permission'] = Permission(request).check_login().check_permission_blog(art, do='edit.delete')
        self.dictionary = dic


# 登陆状态条，就是右上角的那个东西
def login_status(request):
    status = "<a href=\"/account/register\" style=\"float: right;font-size: 12px\">注册</a>" \
                "<a href=\"/account/login\" style=\"float: right;font-size: 12px;padding-right: 3px\">登陆</a>"
    try:    # 获取登陆状态
        uid = int(request.COOKIES.get('UID'))
        user = User.objects.get(uid=uid)
    except BaseException:   # 如果没有登陆
        uid = 0
        user = None
    if uid != 0:    # 登陆状态
        status = "<span style=\"float: right\">" \
                 "欢迎,{0}" \
                 "<a href=\"/account/userHome/\" style=\"padding-left: 5px\">个人主页</a>" \
                 "<a href=\"/account/settings/\" style=\"padding-left: 5px\">设置</a>" \
                 "<a href=\"/account/changePassword/\" style=\"padding-left: 5px\">修改密码</a>" \
                 "<a href=\"/account/logout/\" style=\"padding-left: 5px\">退出</a>" \
                 "</span>".format(user.username)
    return status
