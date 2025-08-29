from django import forms
from .models import Post
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_type', 'title', 'content', 'author']
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        if content is not None and len(content) < 20:
            raise ValidationError({"content": "Описание не может быть менее 20 символов."})
        title = cleaned_data.get("title")
        if title == content:
            raise ValidationError("Описание не должно быть идентичным названию.")
        return cleaned_data
