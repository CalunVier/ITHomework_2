from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
import re
from account.models import User, LoginSession, QuestionList, UserInfo
from .forms import LoginForm, RegisterForm, ForgotPassword, UserSettingForm
from .renders import login_render
from django.core import signing
from permission.permission import Permission
from blog.renders import login_status
from blog.models import ArticleGroups
import datetime


def login(request):

    if request.method == 'GET':
        s = request.GET.get('status')
        # 注册成功时跳入
        if s == '2':
            return render(request, "login.html", {"message": "注册成功", 'login_form': LoginForm()})
        # 密码修改时跳入
        elif s == '3':
            return render(request, "login.html", {"message": "密码修改成功", 'login_form': LoginForm()})

        elif s == '4':
            request.GET.keys()
            return login_render(request, request.GET.keys())
        # 直接访问
        else:
            return render(request, "login.html", {'login_form': LoginForm()})

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.filter(username=username)  # 获取用户
            if user:
                if user[0].password == form.cleaned_data['password']:  # 验证密码
                    response = redirect(reverse("account:UserHome"))    # 创建响应结果以获取
                    now_time = datetime.datetime.now()
                    response.set_cookie("UID", user[0].uid)
                    response.set_signed_cookie("login_key", username, str(now_time))
                    # 写入Session
                    LoginSession(uid=user[0].uid,
                                 login_key=signing.get_cookie_signer(salt="login_key" + str(now_time)).sign(username),
                                 login_time=now_time
                                 ).save()
                    # 更新用户数据
                    user[0].last_login_time = now_time
                    user[0].last_login_ip = request.META['REMOTE_ADDR']
                    user[0].save()
                    return response
        return render(request, "login.html", {"result": "登陆失败", 'login_form': LoginForm()})


def register(request):
    if request.method == 'GET':
        status = request.GET.get('status')
        if status == 1:     # 用户名重复时跳入
            return render(request, "register.html", {"result": '用户名重复', 'reg_form': RegisterForm()})
        else:   # 直接访问时跳入
            return render(request, "register.html", {'reg_form': RegisterForm()})

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 判断注册用户名是否重复
            if User.objects.filter(username=form.cleaned_data['username']):
                return redirect("../register/?status=1")
            # 手动验证表单
            if form.cleaned_data['username'] != "" and \
                    form.cleaned_data['password'] != "" and \
                    re.match(r"^\w+@[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)+$", form.cleaned_data['email']):
                # 写入数据库
                User(username=form.cleaned_data['username'],
                     password=form.cleaned_data['password'],
                     email=form.cleaned_data['email'],
                     question=QuestionList.objects.get(id=int(form.cleaned_data['question'])),
                     answer=form.cleaned_data['answer'],
                     sign_up_ip=request.META['REMOTE_ADDR'],
                     last_login_ip=request.META['REMOTE_ADDR']).save()
                return redirect(reverse("account:Login"))

        return render(request, 'register.html', {"result": '注册失败', 'reg_form': form})


# def permission_checker(request):
#     uid = request.COOKIES.get('UID')
#     try:
#         uid = int(uid)
#     except TypeError:
#         return False
#     session = LoginSession.objects.filter(uid=uid)
#     login_key = request.COOKIES.get('login_key')
#     if session.filter(login_key=login_key):
#         return True
#     return False


def user_home(request, source):
    if Permission(request).check_login().result():
        print("account.views.user_home():初始source:", source)
        if not source:
            source = ''
        if source != 'Favourite':
            source = "UserHome_"+source
            if not re.match('^UserHome_(\d+)', source):
                source = 'UserHome_0'
        user = User.objects.get(uid=int(request.COOKIES.get('UID')))
        groups_db = ArticleGroups.objects.filter(owner=user)
        groups = []
        for g in groups_db:
            groups.append({'gid': g.id, 'group_name': g.group_name})
        print("account.views.user_home():提交source:", source)
        return render(request, "userhome.html",
                      {"UserName": user.username,
                       "login_status": login_status(request),
                       "source": source,
                       "article_group": groups})
    else:
        return render(request, "Permission_Refused.html")


def change_pwd(request):
    if request.method == 'GET':
        if Permission(request).check_login().result():
            uid = request.COOKIES.get("UID")
            user = User.objects.get(uid=uid)
            s = request.GET.get("status")
            if s == '1':
                return render(request, 'changepwd.html', {"username": user.username, "result": "修改密码失败"})
            else:
                return render(request, 'changepwd.html', {"username": user.username})
        else:
            return render(request, "Permission_Refused.html")
    if request.method == 'POST':
        # global login_status
        if Permission(request).check_login().result():
            uid = request.COOKIES.get("UID")
            old_password = request.POST.get("oldp")
            new_password = request.POST.get("newp")
            if uid != '' and old_password != '' and new_password != '':
                print(uid)
                uid = int(uid)
                user = User.objects.get(uid=uid)
                if user.password == old_password:
                    user.password = new_password
                    user.save()
                    ls = LoginSession.objects.filter(uid=uid)
                    for u in ls:
                        u.delete()
                    return redirect('../login/?status=3')
        return redirect('../changePassword/?status=1')


def forgot_password(request):
    if request.method == 'GET':
        # form = QuestionList()
        return render(request, "forgotpwd.html", {'question': ForgotPassword()})
    if request.method == 'POST':
        form = ForgotPassword(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            if str(user.question.id) == form.cleaned_data['question'] and user.answer == form.cleaned_data['answer']:
                user.password = form.cleaned_data['new_password']
                user.save()
                return redirect('../login/?status=3')
        return redirect("../retrievePassword/?status=2")


def logout(request):
    login_key = request.COOKIES.get('login_key')
    LoginSession.objects.filter(login_key=login_key).delete()
    responce = redirect(reverse('Index'))
    responce.delete_cookie('UID')
    responce.delete_cookie('login_key')
    return responce


def settings(request):
    if Permission(request).check_login().result():
        if request.method == 'GET':
            return render(request, "settings.html", {'form': UserSettingForm()})
        if request.method == 'POST':
            form = UserSettingForm(request.POST)
            user = User.objects.get(uid=int(request.COOKIES.get('UID')))
            if form.is_valid():
                UserInfo(uid=user,
                         sex=form.cleaned_data['sex'],
                         phone_number=form.cleaned_data['phone_number'],
                         profile=form.cleaned_data['profile']).save()
            return redirect(reverse("account:UserHome"))

