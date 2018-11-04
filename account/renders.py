from django.shortcuts import render
from .forms import LoginForm

temp_object = {}


def login_render(request, *args):
    c = {'login_form': LoginForm()}
    for a in args:
        try:
            c[a] = temp_object[a]
            temp_object.pop(a)
        finally:
            pass
    return render(request, "login.html", c)


def user_status(request):
    pass
