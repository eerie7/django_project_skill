from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
import redis
import json
from datetime import datetime

# Создаем Redis клиент ДО использования
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


@shared_task
def send_news_notification(user_id, news_title, news_url, category_name=None):
    """Отправка уведомления о новой новости подписчикам"""
    try:
        user = User.objects.get(id=user_id)

        context = {
            'user': user,
            'news_title': news_title,
            'news_url': news_url,
            'category_name': category_name,
            'site_url': 'http://127.0.0.1:8000/',
        }

        # Используем разные шаблоны в зависимости от наличия категории
        if category_name:
            text_content = render_to_string('account/email/news_notification_with_category.txt', context)
            html_content = render_to_string('account/email/news_notification_with_category.html', context)
            subject = f'Новый пост в категории "{category_name}": {news_title}'
        else:
            text_content = render_to_string('account/email/news_notification.txt', context)
            html_content = render_to_string('account/email/news_notification.html', context)
            subject = f'Новая новость: {news_title}'

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # Логируем уведомление
        log_entry = f"{datetime.now().isoformat()}|{user.email}|{news_title}|{category_name or 'No Category'}"
        redis_client.lpush('task:notification_logs', log_entry)
        redis_client.ltrim('task:notification_logs', 0, 499)

        redis_client.incr('task:stats:notifications_sent')

        print(f"✅ Уведомление отправлено для {user.email}")
        return f"✅ Уведомление отправлено для {user.email}"

    except Exception as e:
        redis_client.incr('task:stats:notifications_failed')
        error_message = f"❌ Ошибка отправки уведомления: {e}"
        print(error_message)
        return error_message


# ДОБАВЬТЕ ОСТАЛЬНЫЕ ЗАДАЧИ!

@shared_task(bind=True)
def debug_task(self):
    """Простая тестовая задача для отладки"""
    print(f'🎯 Debug task executed! Request: {self.request!r}')
    return 'DEBUG TASK EXECUTED SUCCESSFULLY'


@shared_task(bind=True, max_retries=3)
def send_single_newsletter(self, user_id):
    """Отправка письма конкретному пользователю"""
    try:
        user = User.objects.get(id=user_id)

        # Логируем начало отправки
        redis_client.lpush('task:email_logs', f"{datetime.now().isoformat()}|START|{user.email}")

        context = {
            'user': user,
            'site_url': 'http://127.0.0.1:8000/',
        }

        text_content = render_to_string('account/weekly_email/weekly_newsletter.txt', context)
        html_content = render_to_string('account/weekly_email/weekly_newsletter.html', context)

        subject = 'С новой неделей! Свежие посты ждут вас!'

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # Логируем успешную отправку
        redis_client.lpush('task:email_logs', f"{datetime.now().isoformat()}|SUCCESS|{user.email}")
        redis_client.incr('task:stats:emails_sent')

        print(f"✅ Отправлено письмо для {user.email}")
        return f"✅ Отправлено для {user.email}"

    except Exception as e:
        redis_client.lpush('task:email_logs', f"{datetime.now().isoformat()}|ERROR|{user_id}|{str(e)}")
        redis_client.incr('task:stats:emails_failed')
        error_message = f"❌ Ошибка отправки для пользователя {user_id}: {e}"
        print(error_message)
        self.retry(countdown=300)


@shared_task(bind=True, max_retries=3)
def send_weekly_newsletter(self):
    """Задача для отправки еженедельной рассылки"""
    try:
        users = User.objects.filter(is_active=True).exclude(email='')
        total_users = users.count()

        print(f"📧 Начинаем рассылку для {total_users} пользователей")

        sent_count = 0
        for user in users:
            try:
                send_single_newsletter.delay(user.id)
                sent_count += 1
            except Exception as e:
                print(f"❌ Ошибка для {user.email}: {e}")

        result_message = f"✅ Рассылка завершена: {sent_count} писем"
        print(result_message)
        return result_message

    except Exception as e:
        error_message = f"❌ Критическая ошибка рассылки: {e}"
        print(error_message)
        self.retry(countdown=600)