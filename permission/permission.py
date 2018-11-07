from account.models import User, LoginSession
from .models import UserPermission
import re


def user_login_checker(request, user):
    session = LoginSession.objects.filter(uid=user.uid)
    login_key = request.COOKIES.get('login_key')
    if session.filter(login_key=login_key):
        return True
    return False


# def user_permission_get(request, user):
#     ps =
#


class Permission(object):
    # allowed默认为True，直到执行check_permission()之前
    allowed = True

    def __init__(self, request):
        # 登陆判定
        try:
            self.user = User.objects.get(uid=int(request.COOKIE.get("UID")))
            self.logged = user_login_checker(request, self.user)
        except BaseException:
            return

    def check_permission(self, need_p):
        # 期待need_p中的字符串将是正则表达式
        permissions = UserPermission.objects.filter(self.user)
        for p in permissions:

            # 对传入的单个字符串权限分析
            if isinstance(need_p, str):
                if re.match(need_p, p):
                    self.allowed = False

            # 对传入的列表权限分析
            elif isinstance(need_p, list):
                check_r = False
                for check_p in need_p:
                    if re.match(check_p, p):
                        check_r = True
                        break
                self.allowed = check_r

    def __call__(self, *args, **kwargs):
        if args != ():
            if isinstance(args[0], list):
                self.check_permission(args[0])
            else:   # 期望是一个need permission列表
                self.check_permission(args)
        return self.result()

    # 返回结果
    def result(self):
        if self.logged and self.allowed:
            return True
        else:
            return False

