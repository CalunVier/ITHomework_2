from django import forms


class NewArticleForm(forms.Form):
    title = forms.CharField(max_length=50, min_length=1, label='标题', widget=forms.TextInput)
    group = forms.CharField(max_length=50, required=False, label='文章分类')
    content = forms.CharField(max_length=500000, label='内容', widget=forms.Textarea)
    visibility = forms.ChoiceField(choices=((0, '公开'), (1, '保护'), (2, '私有')), label='可见度')
    who_can_see = forms.CharField(max_length=200, required=False, label='谁能看')
    who_can_edit = forms.CharField(max_length=200, required=False, label='谁能修改')
    who_can_not_see = forms.CharField(max_length=200, required=False, label='谁不能看')
