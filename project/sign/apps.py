from django.apps import AppConfig


class SignConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sign'

    def ready(self):
        # Импортируем сигналы
        import sign.signals

        # Запускаем планировщик
        self.start_scheduler()

    def start_scheduler(self):
        """Запуск планировщика для рассылки"""
        try:
            from .tasks import start_scheduler
            start_scheduler()
        except ImportError:
            print("Файл tasks.py не найден. Создайте его для работы рассылки.")
        except Exception as e:
            print(f"Ошибка планировщика: {e}")