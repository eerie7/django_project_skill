from django import forms
from .models import Post, Category
from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['post_type', 'title', 'content', 'author', 'categories']

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        if content is not None and len(content) < 20:
            raise ValidationError({"content": "Описание не может быть менее 20 символов."})
        title = cleaned_data.get("title")
        if title == content:
            raise ValidationError("Описание не должно быть идентичным названию.")
        return cleaned_data

    def save(self, commit=True):
        # Сначала сохраняем пост
        post = super().save(commit=commit)
        # Затем сохраняем связи с категориями
        if commit:
            post.categories.set(self.cleaned_data['categories'])
        return post
