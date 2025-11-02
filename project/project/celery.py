import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем Django settings по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Читаем настройки из Django settings с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в файлах tasks.py всех приложений
app.autodiscover_tasks()

# Периодические задачи (beat schedule)
app.conf.beat_schedule = {
    'weekly-newsletter': {
        'task': 'sign.tasks.send_weekly_newsletter',  # ← путь к задаче в приложении sign
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Понедельник 9:00
    },
}

app.conf.timezone = 'Europe/Moscow'

