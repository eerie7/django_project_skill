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
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'rating': [
            'lt',
            'gt',
        ],
    }
