from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
import re
import time
from django.core.signing import BadSignature
from account.models import User,LoginSession, QuestionList
from .forms import LoginForm, RegisterForm, ForgotPassword
from .renders import temp_object, login_render
from django.core import signing

# Create your views here.
# userInfo = [{"username": "root", "password": "123", "email": "admin@admin.com", "question": "rootQuestion", "answer": "rootAnswer"}]
# login_status = []



def login(request):

    if request.method == 'GET':
        s = request.GET.get('status')
        if s == '2':
            return render(request, "login.html", {"message": "注册成功", 'login_form': LoginForm()})
        elif s == '3':
            return render(request, "login.html", {"message": "密码修改成功", 'login_form': LoginForm()})
        elif s == '4':
            request.GET.keys()
            return login_render(request, request.GET.keys())
        else:
            return render(request, "login.html", {'login_form': LoginForm()})

    if request.method == 'POST':
        # 获取输入表单信息
        # username = request.POST.get("username")
        # password = request.POST.get("password")
        # form = LoginForm(request.POST)
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            f = User.objects.filter(username=username)
            if f:
                if f[0].password == form.cleaned_data['password']:
                        response = redirect(reverse("account:UserHome"))
                        now_time = str(time.time())
                        response.set_cookie("UID", f[0].uid)
                        response.set_signed_cookie("login_key", username, now_time)
                        LoginSession(uid=f[0].uid, login_key=signing.get_cookie_signer(salt="login_key" + now_time).sign(username)).save()
                        return response
        return redirect(request, "login.html", {"result": "登陆失败"})

        # for user in userInfo:
        #     if user["username"] == username:
        #         if password == user["password"]:
        #             response = redirect(reverse("account:userHome", args=[username]))
        #             now_time = str(time.time())
        #             response.set_cookie("username", username)
        #             response.set_signed_cookie("login_key", username, now_time)
        #             login_status.append({"username": username, "login_time": now_time})
        #             return response
        # return redirect(request, "login.html", {"result": "登陆失败"})


def register(request):
    if request.method == 'GET':
        status = request.GET.get('status')
        if status == 1:
            return render(request, "regisiter.html", {"result": '用户名重复', 'reg_form': RegisterForm()})
        elif status == 2:
            return render(request, "regisiter.html", {"result": '用户名重复', 'reg_form': RegisterForm()})
        else:
            return render(request, "regisiter.html", {'reg_form': RegisterForm()})
    if request.method == 'POST':
        print('account.views.register POST')
        # username = request.POST.get("username")
        # password = request.POST.get("password")
        # email = request.POST.get("email")
        # question = request.POST.get("question")
        # answer = request.POST.get("answer")
        form = RegisterForm(request.POST)
        if form.is_valid():
            print('account.views.register form.')
            if User.objects.filter(username=form.cleaned_data['username']):
                return redirect("../register/?status=1")

            if form.cleaned_data['username'] != "" and form.cleaned_data['password'] != "" and re.match(r"^\w+@[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)+$", form.cleaned_data['email']):
                # userInfo.append(
                #     {'username': username, 'password': password, "email": email, "question": question, "answer": answer})
                User(username=form.cleaned_data['username'],
                     password=form.cleaned_data['password'],
                     email=form.cleaned_data['email'],
                     question=QuestionList.objects.get(id=int(form.cleaned_data['question'])+1),
                     answer=form.cleaned_data['answer'],
                     sign_up_ip=request.META['REMOTE_ADDR'],
                     last_login_ip=request.META['REMOTE_ADDR']).save()
                return redirect("../login/?status=2")

        return redirect("../register/?status=2")


def permission_checker(request):
    uid = request.COOKIES.get('UID')
    session = LoginSession.objects.filter(uid=int(uid))
    login_key = request.COOKIES.get('login_key')
    if session.filter(login_key=login_key):
        return True
    return False


# def check_user(request):
#     if permission_checker(request):
#         return render(request, "check.html", {"userInfo": userInfo, "loginedUser": login_status})
#     else:
#         return render(request, "Permission_Refused.html")


def user_home(request):
    if permission_checker(request):
        return render(request, "userhome.html", {"UserName": User.objects.get(uid=int(request.COOKIES.get('UID'))).username})
    else:
        return render(request, "Permission_Refused.html")


def change_pwd(request):
    if request.method == 'GET':
        if permission_checker(request):
            username = request.COOKIES.get("username")
            s = request.GET.get("status")
            if s == '1':
                return render(request, 'changepwd.html', {"username": username, "result": "修改密码失败"})
            else:
                return render(request, 'changepwd.html', {"username": username})
        else:
            return render(request, "Permission_Refused.html")
    if request.method == 'POST':
        # global login_status
        if permission_checker(request):
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
                # for info in userInfo:
                #     if username == info["username"]:
                #         if old_password == info["password"]:
                #             info["password"] = new_password
                #             temp_status = list(login_status)
                #             for s in login_status:
                #                 if username == s["username"]:
                #                     temp_status.remove(s)
                #             login_status = temp_status
                #             return redirect('../login/?status=3')
                #         break
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

    # 完全看不懂这里的逻辑
    # if request.method == 'GET':
    #     status = request.GET.get('status')
    #     if status == "1":
    #         username = request.GET.get("username")
    #         for info in userInfo:
    #             if username == info["username"]:
    #                 if info['question'] != "如不填写，将无法找回密码" and info['question'] != "":
    #                     return render(request, "forgotpwd.html", {"username": username, "question": info["question"]})
    #                 break
    #         return render(request, "forgotpwd.html", {"question": "没有找到密保问题"})
    #     elif status == "2":
    #         return render(request, "forgotpwd.html", {"result": "找回失败"})
    #     else:
    #         return render(request, "forgotpwd.html")
    # else:
    #     if request.POST.get("getQuestion"):
    #         return redirect("../retrievePassword/?status=1&username={0}".format(request.POST.get("username")))
    #     else:
    #         username = request.POST.get("username")
    #         answer = request.POST.get("answer")
    #         for info in userInfo:
    #             if username == info["username"]:
    #                 if answer == info["answer"] and info['question'] != "如不填写，将无法找回密码" and info['question'] != "":
    #                     info["password"] = request.POST.get("newpwd")
    #                     return redirect('../login/?status=3')
    #                 break
    #         return redirect("../retrievePassword/?status=2")


# def retrieve_password(request):
#     status = request.GET.get("status")
#     if status == "1":
#         username = request.GET.get("username")
#         for info in userInfo:
#             if username == info["username"]:
#                 if info['question'] != "如不填写，将无法找回密码" and info['question'] != "":
#                     return render(request, "forgotpwd.html", {"username": username, "question": info["question"]})
#                 break
#         return render(request, "forgotpwd.html", {"question": "没有找到密保问题"})
#     elif status == "2":
#         return render(request, "forgotpwd.html", {"result": "找回失败"})
#     else:
#         return render(request, "forgotpwd.html")


# def to_retrieve_password(request):
#     if request.POST.get("getQuestion"):
#         return redirect("../retrievePassword/?status=1&username={0}".format(request.POST.get("username")))
#     else:
#         username = request.POST.get("username")
#         answer = request.POST.get("answer")
#         for info in userInfo:
#             if username == info["username"]:
#                 if answer == info["answer"] and info['question'] != "如不填写，将无法找回密码" and info['question'] != "":
#                     info["password"] = request.POST.get("newpwd")
#                     return redirect('../login/?status=3')
#                 break
#         return redirect("../retrievePassword/?status=2")


def logout(request):

    return redirect("../login/")


# def to_logout(request):
#
#     pass

    # username = request.COOKIES.get("username")
    # login_times = []
    # for u in login_status:
    #     if username == u['username']:
    #         login_times.append(u["login_time"])
    # for t in login_times:
    #     try:
    #         login_key = request.get_signed_cookie("login_key", salt=t)
    #     except BadSignature:
    #         login_key = ''
    #     if login_key == username:
    #         for u in login_status:
    #             if u["login_time"] == t:
    #                 login_status.remove(u)
    #                 return


def settings(request):
    pass