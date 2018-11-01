from django import forms
from .models import QuestionList


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=3, label='用户名')
    password = forms.CharField(16, 3, widget=forms.PasswordInput, label='密码')


def get_question():
    q_list = QuestionList.objects.all()
    qt = []
    for q in q_list:
        qt.append((q.id, q.question))
    return tuple(qt)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=3, label='用户名')
    password = forms.CharField(16, 3, widget=forms.PasswordInput, label='密码')
    email = forms.EmailField(label='电子邮箱')
    question = forms.ChoiceField(choices=get_question(), label='密保问题')
    answer = forms.CharField(max_length=40, min_length=2, label='答案')


class ForgotPassword(forms.Form):
    username = forms.CharField(max_length=20, min_length=3, label='用户名')
    question = forms.ChoiceField(choices=get_question(), label='密保问题')
    answer = forms.CharField(max_length=40, min_length=2, label='答案')
    new_password = forms.CharField(16, 3, widget=forms.PasswordInput, label='新密码')
