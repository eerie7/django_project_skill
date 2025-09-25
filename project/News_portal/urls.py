from django.urls import path
from .views import PostsList, AuthorList, CategoryList, CommentsList, AuthorDetail, PostDetail, PostCreate, PostUpdate, \
    PostDelete

urlpatterns = [
    path('authors/', AuthorList.as_view(), name='authors'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('posts/', PostsList.as_view(), name='posts'),
    path('comments/', CommentsList.as_view(), name='comments'),
    path('authors/<int:pk>/', AuthorDetail.as_view(), name='author_detail'),
    path('news/<int:pk>/', PostDetail.as_view(), name='news_detail'),
    path('articles/<int:pk>/', PostDetail.as_view(), name='articles_detail'),
    path('post/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('posts/create/', PostCreate.as_view(), name='post_create'),
    path('news/<int:pk>/update/', PostUpdate.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/<int:pk>/update/', PostUpdate.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
]
