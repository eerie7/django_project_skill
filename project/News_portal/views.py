from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Author, Category, Comment



class AuthorList(ListView):
    model = Author
    ordering = 'author_name'
    template_name = 'authors.html'
    context_object_name = 'authors'

class AuthorDetail(DetailView):
    model = Author
    template_name = 'author.html'
    context_object_name = 'author'


class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-date'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'


class CategoryList(ListView):
    model = Category
    ordering = 'category_name'
    template_name = 'categories.html'
    context_object_name = 'categories'


class CommentsList(ListView):
    model = Comment
    ordering = 'comment'
    template_name = 'comments.html'
    context_object_name = 'comments'

class PostDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


