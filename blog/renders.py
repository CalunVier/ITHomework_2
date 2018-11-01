from django.shortcuts import render


def article_list_render(request, articles):
    c = {'articles': articles}
    return render(request, "article_list.html", c)
