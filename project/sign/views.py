from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from News_portal.models import Author, Category, CategorySubscription
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from News_portal.models import Category, CategorySubscription
from .tasks import send_news_notification  # Импортируем Celery задачу
from django.urls import reverse
from django.core.cache import cache
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


def logout_view(request):
    logout(request)
    return redirect('sign_home')


def sign_view(request):
    # Получаем категории для личного кабинета
    all_categories = Category.objects.all()

    if request.user.is_authenticated:
        subscribed_category_ids = CategorySubscription.objects.filter(
            user=request.user
        ).values_list('category_id', flat=True)
        subscribed_categories = Category.objects.filter(id__in=subscribed_category_ids)
        available_categories = Category.objects.exclude(id__in=subscribed_category_ids)
        is_not_author = not hasattr(request.user, 'author')
    else:
        subscribed_categories = []
        available_categories = all_categories
        is_not_author = True

    return render(request, 'sign/home.html', {
        'all_categories': all_categories,
        'subscribed_categories': subscribed_categories,
        'available_categories': available_categories,
        'is_not_author': is_not_author,
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('sign_home')
    else:
        form = AuthenticationForm()
    return render(request, 'sign/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'sign/signup.html', {'form': form})


@login_required
def upgrade_me(request):
    # Получаем или создаем группу авторов
    authors_group, created = Group.objects.get_or_create(name='authors')

    # Проверяем не является ли пользователь уже автором
    if not request.user.groups.filter(name='authors').exists():
        # Добавляем пользователя в группу авторов
        authors_group.user_set.add(request.user)

        # Создаем профиль автора
        Author.objects.get_or_create(
            user=request.user,
            defaults={'author_name': request.user.username}
        )
    else:
        # Если уже автор, но нет профиля - создаем
        if not hasattr(request.user, 'author'):
            Author.objects.create(
                user=request.user,
                author_name=request.user.username
            )

    return redirect('sign_home')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем ID категорий, на которые пользователь подписан
        subscribed_category_ids = CategorySubscription.objects.filter(
            user=self.request.user
        ).values_list('category_id', flat=True)

        # Получаем объекты категорий
        subscribed_categories = Category.objects.filter(id__in=subscribed_category_ids)

        # Все категории
        all_categories = Category.objects.all()

        # Категории, на которые НЕ подписан
        available_categories = Category.objects.exclude(id__in=subscribed_category_ids)

        # Проверяем, является ли пользователь автором
        is_not_author = not hasattr(self.request.user, 'author')

        context.update({
            'subscribed_categories': subscribed_categories,
            'all_categories': all_categories,
            'available_categories': available_categories,  # Добавляем доступные категории
            'is_not_author': is_not_author,
        })

        # Отладочная информация
        print("Все категории:", list(all_categories))
        print("Подписанные ID:", list(subscribed_category_ids))
        print("Доступные категории:", list(available_categories))

        return context


@login_required
def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subscription, created = CategorySubscription.objects.get_or_create(
        user=request.user,
        category=category
    )
    if created:
        print(f"Пользователь {request.user} подписался на {category}")

        # Отправляем приветственное письмо при подписке (асинхронно)
        try:
            send_news_notification.delay(
                request.user.id,
                f"Добро пожаловать в категорию {category.name}",
                f"http://127.0.0.1:8000{reverse('category_news', args=[category.id])}"
            )
            print(f"Приветственное письмо поставлено в очередь для {request.user.email}")
        except Exception as e:
            print(f"Ошибка постановки приветственного письма в очередь: {e}")

    return redirect('sign_home')


@login_required
def unsubscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    deleted_count = CategorySubscription.objects.filter(
        user=request.user,
        category=category
    ).delete()[0]

    if deleted_count > 0:
        print(f"Пользователь {request.user} отписался от {category}")

    return redirect('sign_home')


# Дополнительная функция для отправки уведомлений при создании новости
# Эту функцию нужно будет вызвать из вашего приложения News_portal при создании новости
def notify_subscribers_about_new_news(news_instance):
    """
    Функция для отправки уведомлений подписчикам категории о новой новости
    Вызывается из приложения News_portal при создании/публикации новости
    """
    try:
        # Получаем категории новости
        news_categories = news_instance.category.all()

        for category in news_categories:
            # Получаем всех подписчиков этой категории
            subscribers = CategorySubscription.objects.filter(category=category)

            for subscription in subscribers:
                # Отправляем уведомление каждому подписчику асинхронно
                send_news_notification.delay(
                    subscription.user.id,
                    news_instance.title,
                    f"http://127.0.0.1:8000{news_instance.get_absolute_url()}"
                )

        print(f"Уведомления о новости '{news_instance.title}' поставлены в очередь")

    except Exception as e:
        print(f"Ошибка при постановке уведомлений в очередь: {e}")


def is_staff_user(user):
    return user.is_staff


@user_passes_test(is_staff_user)
def celery_monitor_dashboard(request):
    """Веб-дашборд для мониторинга Celery"""
    context = {}

    # Собираем статистику
    context['emails_sent'] = cache.get('task:stats:emails_sent') or 0
    context['emails_failed'] = cache.get('task:stats:emails_failed') or 0
    context['notifications_sent'] = cache.get('task:stats:notifications_sent') or 0
    context['notifications_failed'] = cache.get('task:stats:notifications_failed') or 0

    # Последние логи
    email_logs = cache.lrange('task:email_logs', 0, 49) or []
    context['recent_email_logs'] = [log.decode('utf-8') if isinstance(log, bytes) else log for log in email_logs[:10]]

    return render(request, 'sign/celery_monitor.html', context)


@user_passes_test(is_staff_user)
def celery_monitor_api(request):
    """API для мониторинга (для AJAX)"""
    stats = {
        'emails_sent': cache.get('task:stats:emails_sent') or 0,
        'emails_failed': cache.get('task:stats:emails_failed') or 0,
        'notifications_sent': cache.get('task:stats:notifications_sent') or 0,
        'notifications_failed': cache.get('task:stats:notifications_failed') or 0,
    }
    return JsonResponse(stats)