from django import forms


class NewArticleForm(forms.Form):
    title = forms.CharField(max_length=50, min_length=1, label='标题', widget=forms.TextInput)
    content = forms.CharField(max_length=500000, label='内容', widget=forms.Textarea)
