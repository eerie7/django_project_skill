# News_portal/signals.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post, CategorySubscription
from django.urls import reverse


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers(sender, instance, action, **kwargs):
    """
    Отправляет уведомления когда к посту добавляются категории
    """
    print(f"🔔 СИГНАЛ ВЫЗВАН! Action: {action}, Пост: {instance.title}")

    if action == "post_add":  # ← ТОЛЬКО ЭТО УСЛОВИЕ, БЕЗ is_published!
        print(f"🎯 ДЕТЕКТИРОВАН post_add! Запускаем рассылку для поста: {instance.title}")

        # Ленивый импорт для избежания циклических зависимостей
        from sign.tasks import send_news_notification

        # Получаем категории поста
        post_categories = instance.categories.all()
        print(f"📋 Категории поста: {[c.category_name for c in post_categories]}")

        # Для каждой категории находим подписчиков
        for category in post_categories:
            subscriptions = CategorySubscription.objects.filter(category=category)
            print(f"👥 Подписчики категории {category}: {subscriptions.count()}")

            for subscription in subscriptions:
                # Отправляем уведомление через Celery (асинхронно)
                try:
                    send_news_notification.delay(
                        subscription.user.id,
                        instance.title,
                        f"http://127.0.0.1:8000{reverse('post_detail', args=[instance.id])}",
                        category.get_category_name_display()
                    )
                    print(f"✅ Уведомление в очереди для: {subscription.user.email}")
                except Exception as e:
                    print(f"❌ Ошибка постановки уведомления: {e}")
    else:
        print(f"⚡ Сигнал вызван с action: {action} (не post_add)")


def send_post_notification(post, user, category):
    """Отправляет HTML email уведомление о новом посте (синхронная версия)"""
    # Эта функция может остаться для синхронной отправки
    pass