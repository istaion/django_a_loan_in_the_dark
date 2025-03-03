from django import forms
from news.models import New

class_for_css = 'form-control'

class NewsForm(forms.ModelForm):
    class Meta:
        model = New
        fields = ['title', 'content', 'picture']

class EditNewsForm(forms.ModelForm):
    class Meta:
        model = New
        fields = ['title', 'content', 'picture']
        widgets = {
            'title': forms.TextInput(attrs={'class': class_for_css}),
            'content': forms.TextInput(attrs={'class': class_for_css}),
        }