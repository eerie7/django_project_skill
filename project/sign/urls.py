from django.urls import path, include
from . import views
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView

class GoogleLogin(OAuth2LoginView):
    adapter_class = GoogleOAuth2Adapter


urlpatterns = [
    path('', views.sign_view, name='sign_home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('upgrade/', views.upgrade_me, name='upgrade'),

    # ДОБАВЛЯЕМ ПУТИ ДЛЯ ПОДПИСКИ
    path('subscribe/<int:category_id>/', views.subscribe_category, name='subscribe_category'),
    path('unsubscribe/<int:category_id>/', views.unsubscribe_category, name='unsubscribe_category'),

    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('accounts/', include('allauth.urls')),
    path('socialaccounts/', include('allauth.socialaccount.urls')),
]