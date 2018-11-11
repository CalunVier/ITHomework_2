from account.models import User, LoginSession
from .models import UserPermission
import re, datetime


def user_login_checker(request, user):
    session = LoginSession.objects.filter(uid=user.uid)
    login_key = request.COOKIES.get('login_key')
    if session.filter(login_key=login_key):
        return True
    return False


def user_permission_add(user, permission):
    UserPermission(user=user, permission=r'^'+permission.replace('.', '\.')+r'(.)*').save()
    print(user.username, "add permission:"r'^'+permission.replace('.', '\.')+r'(.)*')


class Permission(object):
    # logged默认为False，知道执行check_login()之前
    # allowed默认为True，直到执行check_permission()之前
    allowed = True

    def __init__(self, request, logged=False):
        self.request = request
        self.logged = logged
        try:
            self.user = User.objects.get(uid=int(self.request.COOKIES.get("UID")))
        except BaseException:
            self.user = User(uid=0, username='Null')
        self.default_permission = [
                                   r"^account\.{0}(.)*".format(self.user.username),
                                   r"^blog\.Visibility\.PUBLIC$"
                                   ]

    # 检查登录状态
    def check_login(self):
        # self.logged = user_login_checker(self.request, self.user)
        print(self.user.uid)
        session = LoginSession.objects.filter(uid=self.user.uid)
        print(session)
        # 删除过期Session
        invalid_session = session.filter(login_time__lt=(datetime.datetime.now()-datetime.timedelta(days=2)))
        if invalid_session:
            # 因为按顺序加入，认为之前的Session全部失效
            LoginSession.objects.filter(uid__lt=invalid_session[len(invalid_session)-1].uid).delete()

        login_key = self.request.COOKIES.get('login_key')
        print('COOKIE:login_key:', login_key)
        print(session.filter(login_key=login_key))
        if session.filter(login_key=login_key):
            self.logged = True
        else:
            self.logged = False
        return self

    def check_permission(self, need_p, not_p):
        debug_source = 'Permission.check_permission:'
        # 期待need_p中的字符串将是正则表达式
        check_result = False
        # 默认权限检查
        print(debug_source+'用户默认权限检查')
        for dp in self.default_permission:
            # 对传入的单个字符串权限分析
            if isinstance(need_p, str):
                print(debug_source + '对传入的单个字符串权限分析')
                if re.match(dp, need_p):
                    print(debug_source + '检查权限:' + need_p + '通过')
                    check_result = True
                    break
                else:
                    print(debug_source+'检查权限:'+need_p+'失败')
            # 对传入的列表权限分析
            elif isinstance(need_p, list):
                print(debug_source + '对传入的列表权限分析')
                for check_p in need_p:
                    if re.match(dp, check_p):
                        print(debug_source + "用" + dp + '检查权限:' + check_p + '通过')
                        check_result = True
                        break
                    else:
                        print(debug_source + "用" + dp + '检查权限:' + check_p + '失败')

        # 一般权限检查
        permissions_allow = UserPermission.objects.filter(user=self.user, rule=0)
        if not check_result:
            print(debug_source+'一般权限检查')
            for p in permissions_allow:
                # 对传入的单个字符串权限分析
                if isinstance(need_p, str):
                    print(debug_source + '对传入的单个字符串权限分析')
                    if re.match(p.permission, need_p):
                        print(debug_source + "用" + p.permission + '检查权限:' + need_p + '通过')
                        check_result = True
                        break
                    else:
                        print(debug_source + "用" + p.permission + '检查权限:' + need_p + '失败')
                # 对传入的列表权限分析
                elif isinstance(need_p, list):
                    print(debug_source + '对传入的列表权限分析')
                    for check_p in need_p:
                        if re.match(p.permission, check_p):
                            print(debug_source + "用" + p.permission + '检查权限:' + check_p + '通过')
                            check_result = True
                            break
                        else:
                            print(debug_source + "用" + p.permission + '检查权限:' + check_p + '失败')

            # 反向权限检查
            permissions_not_allow = UserPermission.objects.filter(user=self.user, rule=1)
            print(debug_source + '反向权限检查')
            for np in permissions_not_allow:
                # 对传入的单个字符串权限分析
                if isinstance(not_p, str):
                    print(debug_source + '对传入的单个字符串权限分析')
                    if re.match(np.permission, not_p):
                        print(debug_source + "用" + np.permission + '检查权限:' + not_p + '存在')
                        check_result = False
                        break
                    else:
                        print(debug_source + "用" + np.permission + '检查权限:' + not_p + '不存在')
                # 对传入的列表权限分析
                elif isinstance(not_p, list):
                    print(debug_source + '对传入的列表权限分析')
                    for check_p in not_p:
                        if re.match(np.permission, check_p):
                            print(debug_source + "用" + np.permission + '检查权限:' + check_p + '存在')
                            check_result = False
                            break
                        else:
                            print(debug_source + "用" + np.permission + '检查权限:' + check_p + '不存在')

            self.allowed = check_result
        return self

    # 访问博客专用的检查函数
    def check_permission_blog(self, art, do, need_p=None, not_p=None):
        if not need_p:
            need_p = []
        if not not_p:
            not_p = []
        # 作者免检
        print(r'Permission.check_permission_blog():art.author:', art.author, "self.user.username:",self.user.username)
        if art.author.username == self.user.username:
            print(r'Permission.check_permission_blog:作者访问')
            return self
        if do == 'view' or do == 'comment':
            if art.Visibility == 0:
                print(r'Permission.check_permission_blog:文章要求blog.Visibility.PUBLIC权限')
                need_p.append('blog.Visibility.PUBLIC')
            elif art.Visibility == 1:
                print(r'Permission.check_permission_blog:文章要求blog.Visibility.PROTECT权限')
                need_p.append('blog.Visibility.PROTECT')
        need_p.append('blog.{0}.{1}'.format(art.aid, do))
        not_p.append('blog.{0}.{1}'.format(art.aid, do))
        print("Permission.check_permission_blog:需检查权限:"+str(need_p))
        return self.check_permission(need_p, not_p)

    # 直接调用时
    def __call__(self, *args, **kwargs):
        if args != ():
            if isinstance(args[0], list):
                self.check_permission(args[0])
            else:   # 期望是一个need permission列表
                self.check_permission(args)
        return self.result()

    # 返回结果
    def result(self):
        debug_source = 'Permission.result:'
        print(debug_source, self.logged, self.allowed)
        if self.logged and self.allowed:
            return True
        else:
            return False
