import django_filters
from django_filters import FilterSet
from .models import Post

# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
from django_filters import FilterSet, CharFilter, NumberFilter, ModelChoiceFilter
from .models import Post, Category
from django.db.models import Q


class PostFilter(FilterSet):
    category = ModelChoiceFilter(
        field_name='categories',  # поле ManyToMany связи
        queryset=Category.objects.all(),
        label='Категория',
        empty_label='Все категории'
    )
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'rating': [
            'lt',
            'gt',
        ],
    }
