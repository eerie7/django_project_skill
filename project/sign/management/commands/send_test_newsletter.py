from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


class Command(BaseCommand):
    help = 'Send test weekly newsletter to specific user or all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Send to specific username',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Send to specific email',
        )

    def handle(self, *args, **options):
        # Определяем кому отправлять
        if options['username']:
            users = User.objects.filter(username=options['username'])
        elif options['email']:
            users = User.objects.filter(email=options['email'])
        else:
            # Отправляем себе или тестовому пользователю
            users = User.objects.filter(is_active=True)[:1]  # первому активному

        for user in users:
            self.send_newsletter(user)
            self.stdout.write(
                self.style.SUCCESS(f'Письмо отправлено для {user.username} ({user.email})')
            )

    def send_newsletter(self, user):
        """Функция отправки письма"""
        context = {
            'user': user,
            'site_url': 'http://localhost:8000',  # или ваш домен
        }

        html_content = render_to_string('account/email/weekly_newsletter.html', context)
        subject = 'ТЕСТ: С новой неделей! Свежие посты ждут вас!'

        msg = EmailMultiAlternatives(
            subject=subject,
            body='Текстовая версия письма',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()