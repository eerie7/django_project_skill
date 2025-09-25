from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post, CategorySubscription


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers(sender, instance, action, **kwargs):
    """
    Отправляет уведомления когда к посту добавляются категории
    """
    if action == "post_add":
        # Получаем категории поста
        post_categories = instance.categories.all()

        # Для каждой категории находим подписчиков
        for category in post_categories:
            subscriptions = CategorySubscription.objects.filter(category=category)

            for subscription in subscriptions:
                # Отправляем email каждому подписчику
                send_post_notification(instance, subscription.user, category)


def send_post_notification(post, user, category):
    """Отправляет HTML email уведомление о новом посте"""
    # Получаем HTML содержимое
    html_content = render_to_string(
        'emails/post_category_subscribe.html',
        {
            'post': post,
            'user': user,
            'category': category,
        }
    )

    # Создаем письмо
    msg = EmailMultiAlternatives(
        subject=f'Новый пост в категории "{category.get_category_name_display()}"',
        body=f'Пост: {post.title}\nАвтор: {post.author.author_name}\n{post.preview()}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()