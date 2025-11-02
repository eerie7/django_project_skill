from django.core.management.base import BaseCommand
import json
from datetime import datetime
import redis


class Command(BaseCommand):
    help = 'Мониторинг Celery задач'

    def __init__(self):
        super().__init__()
        # Подключаемся к Redis напрямую
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все логи и статистику',
        )

    def handle(self, *args, **options):
        print("🎯 МОНИТОРИНГ CELERY (прямое подключение к Redis)")

        # Проверяем подключение к Redis
        try:
            self.redis.ping()
            print("✅ Redis подключен успешно")
        except Exception as e:
            print(f"❌ Ошибка подключения к Redis: {e}")
            return

        if options['clear']:
            self.clear_stats()
            return

        self.show_overview()

    def clear_stats(self):
        """Очистка всей статистики"""
        try:
            # Находим все ключи связанные с задачами
            keys = self.redis.keys('task:*')
            if keys:
                self.redis.delete(*keys)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Очищено {len(keys)} ключей статистики')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Ключи для очистки не найдены')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка очистки: {e}')
            )

    def safe_get(self, key, default=0):
        """Безопасное получение значения"""
        try:
            value = self.redis.get(key)
            return int(value) if value is not None else default
        except:
            return default

    def safe_lrange(self, key, start, end):
        """Безопасное получение списка из Redis"""
        try:
            return self.redis.lrange(key, start, end)
        except:
            return []

    def show_overview(self):
        """Общая статистика"""
        self.stdout.write("\n🎯 МОНИТОРИНГ CELERY + REDIS")
        self.stdout.write("=" * 50)

        # Общая статистика
        emails_sent = self.safe_get('task:stats:emails_sent')
        emails_failed = self.safe_get('task:stats:emails_failed')
        notifications_sent = self.safe_get('task:stats:notifications_sent')
        notifications_failed = self.safe_get('task:stats:notifications_failed')

        self.stdout.write(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        self.stdout.write(f"   📧 Писем отправлено: {emails_sent}")
        self.stdout.write(f"   ❌ Ошибок отправки: {emails_failed}")
        self.stdout.write(f"   🔔 Уведомлений отправлено: {notifications_sent}")
        self.stdout.write(f"   ❌ Ошибок уведомлений: {notifications_failed}")

        # Статистика по еженедельной рассылке
        last_stats_json = self.redis.get('task:weekly_newsletter:last_stats')
        if last_stats_json:
            try:
                last_stats = json.loads(last_stats_json)
                self.stdout.write(f"\n📨 ПОСЛЕДНЯЯ РАССЫЛКА:")
                self.stdout.write(f"   ✅ Отправлено писем: {last_stats.get('sent_count', 0)}")
                self.stdout.write(f"   ❌ Ошибок: {last_stats.get('error_count', 0)}")
                self.stdout.write(f"   👥 Всего пользователей: {last_stats.get('total_users', 0)}")
                self.stdout.write(f"   ⏰ Завершена: {last_stats.get('completed_at', 'N/A')}")
            except json.JSONDecodeError:
                self.stdout.write(f"\n📨 ПОСЛЕДНЯЯ РАССЫЛКА: Данные повреждены")

        # Последние логи email
        email_logs = self.safe_lrange('task:email_logs', 0, 9)
        if email_logs:
            self.stdout.write(f"\n📋 ПОСЛЕДНИЕ EMAIL ЛОГИ:")
            for log in reversed(email_logs):
                parts = log.split('|')
                if len(parts) >= 3:
                    status_icon = '✅' if parts[1] == 'SUCCESS' else '🟡' if parts[1] == 'START' else '❌'
                    self.stdout.write(f"   {status_icon} {parts[0]} - {parts[2]}")
        else:
            self.stdout.write(f"\n📋 ПОСЛЕДНИЕ EMAIL ЛОГИ: Логов нет")

        # Информация о Redis
        try:
            redis_info = self.redis.info()
            self.stdout.write(f"\n🗃️  REDIS ИНФОРМАЦИЯ:")
            self.stdout.write(f"   💾 Использовано памяти: {redis_info.get('used_memory_human', 'N/A')}")
            self.stdout.write(f"   📊 Подключений: {redis_info.get('connected_clients', 'N/A')}")
            self.stdout.write(f"   📈 БД 1 ключей: {self.redis.dbsize()}")
        except Exception as e:
            self.stdout.write(f"\n🗃️  Информация Redis недоступна: {e}")

        # Проверяем очередь Celery (БД 0)
        try:
            celery_redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            queue_length = celery_redis.llen('celery')
            self.stdout.write(f"\n🔮 ОЧЕРЕДЬ CELERY:")
            self.stdout.write(f"   📥 Задач в очереди: {queue_length}")
        except Exception as e:
            self.stdout.write(f"\n🔮 Очередь Celery недоступна: {e}")

        # Рекомендации
        self.stdout.write(f"\n💡 СТАТУС:")
        self.stdout.write(f"   ✅ Redis подключен напрямую")
        self.stdout.write(f"   📊 Статистика обновляется в реальном времени")
        self.stdout.write(f"   🔧 Используйте --clear для очистки статистики")