from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import PostForm
from .filters import PostFilter
from .models import Post, Author, Category, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CategorySubscription
from sign.views import notify_subscribers_about_new_news  # ← ТОЛЬКО ЭТОТ ИМПОРТ!


class AuthorList(LoginRequiredMixin, ListView):
    model = Author
    ordering = 'author_name'
    template_name = 'authors.html'
    context_object_name = 'authors'
    paginate_by = 15
    login_url = '/accounts/login/'


class AuthorDetail(LoginRequiredMixin, DetailView):
    model = Author
    template_name = 'author.html'
    context_object_name = 'author'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        selected_category = self.request.GET.get('category')
        if selected_category:
            context['posts'] = self.object.post_set.filter(categories__id=selected_category)
        else:
            context['posts'] = self.object.post_set.all()

        return context


class PostsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    login_url = '/accounts/login/'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class CategoryList(LoginRequiredMixin, ListView):
    model = Category
    ordering = 'category_name'
    template_name = 'categories.html'
    context_object_name = 'categories'
    login_url = '/accounts/login/'


class CommentsList(LoginRequiredMixin, ListView):
    model = Comment
    ordering = 'comment'
    template_name = 'comments.html'
    context_object_name = 'comments'
    login_url = '/accounts/login/'


class PostDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    login_url = '/accounts/login/'


class PostCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('News_portal.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('sign_home')
    login_url = '/accounts/login/'

    def form_valid(self, form):
        # Устанавливаем автора как текущего пользователя
        form.instance.author = self.request.user.author

        # Сохраняем форму
        response = super().form_valid(form)

        # ОДНА СТРОЧКА - отправляем уведомления подписчикам
        notify_subscribers_about_new_news(self.object)

        return response


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('News_portal.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    login_url = '/accounts/login/'

    def get_success_url(self):
        return reverse_lazy('author_detail', kwargs={'pk': self.object.author.pk})


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('News_portal.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    login_url = '/accounts/login/'

    def get_success_url(self):
        return reverse_lazy('author_detail', kwargs={'pk': self.object.author.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.object.post_type
        return context
