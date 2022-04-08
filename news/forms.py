from django import forms

from .models import *


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['author_id'].empty_label = 'Выберите автора...'

    class Meta:
        model = Post
        fields = ['header', 'text', 'categories', 'author_id']
        labels = {
            'header': 'Заголовок публикации',
            'text': 'Текст публикации',
            'categories': 'Категории',
            'author_id': 'Автор',
        }