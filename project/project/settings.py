"""
Django settings for project project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^jmz$-+*p5jch!f91nyrpo@*aa+kw@-so)=-*ws7@7(93e@f%5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    # Ваши приложения
    'fpages',
    'News_portal',
    'django_filters',
    'sign',
    'protect',

    # allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Провайдеры
    'allauth.socialaccount.providers.google',

    'django_apscheduler'
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # обязательно для allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== НАСТРОЙКИ ALIAUTH ДЛЯ КРАСИВЫХ СТРАНИЦ ====================

# Перенаправления
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/sign/'  # после входа - на вашу красивую страницу профиля
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'  # после выхода - на красивую страницу
LOGOUT_REDIRECT_URL = '/sign/logout-success/'  # дублирующая настройка

# Настройки аккаунта
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True  # лучше оставить True для красоты
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # можно входить и по email и по username
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7

# Дополнительные настройки для удобства
ACCOUNT_SESSION_REMEMBER = True  # запоминать пользователя
ACCOUNT_LOGOUT_ON_GET = True  # выход по GET запросу (для простоты)
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Ваш Сайт] '  # префикс для писем

# Кастомные формы для красивых страниц
ACCOUNT_FORMS = {
    'login': 'sign.forms.CustomLoginForm',
    'signup': 'sign.forms.CustomSignupForm',
    'change_password': 'sign.forms.CustomChangePasswordForm',
    'reset_password': 'sign.forms.CustomResetPasswordForm',
    'set_password': 'sign.forms.CustomSetPasswordForm',
    'add_email': 'sign.forms.CustomAddEmailForm',
}

# Настройки Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': '810991253749-ds3pr7fbusmiidcfnu5c79eql1qir89d.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        }
    }
}

# Дополнительные настройки для socialaccount
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = False

# Настройки email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'Pozetuve04@yandex.ru'
EMAIL_HOST_PASSWORD = 'jreryiebtjhlvsjg'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'Pozetuve04@yandex.ru'
SERVER_EMAIL = 'Pozetuve04@yandex.ru'

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"


APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds