from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit


def send_weekly_newsletter():
    """Функция для отправки еженедельной рассылки"""

    # Получаем всех активных пользователей
    users = User.objects.filter(is_active=True)

    for user in users:
        # Контекст для шаблона
        context = {
            'user': user,
            'site_url': 'http://ваш-сайт.com',  # замените на ваш домен
        }

        # Рендерим HTML шаблон
        html_content = render_to_string('emails/weekly_newsletter.html', context)
        subject = 'С новой неделей! Свежие посты ждут вас!'

        # Создаем email
        msg = EmailMultiAlternatives(
            subject=subject,
            body='',  # текстовую версию можно добавить отдельно
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
            print(f"Отправлено письмо для {user.email}")
        except Exception as e:
            print(f"Ошибка отправки для {user.email}: {e}")


def start_scheduler():
    """Запуск планировщика"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore('django')

    # Добавляем задачу (каждый понедельник в 9:00 утра)
    scheduler.add_job(
        send_weekly_newsletter,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='weekly_newsletter',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()

    # Останавливаем планировщик при выходе
    atexit.register(lambda: scheduler.shutdown())