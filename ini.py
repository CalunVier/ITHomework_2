from account.models import QuestionList,User
from blog.models import ArticlesList

QuestionList(question='Question1').save()
QuestionList(question='Question2').save()
QuestionList(question='Question3').save()
i = 100
while i < 100:
    ArticlesList(article_name='Article'+str(i), content='ArticleContent', article_address='TestContent', auther=User.objects.get(uid=1)).save()
    i += 1



