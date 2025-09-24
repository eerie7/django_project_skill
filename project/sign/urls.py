from django.urls import path, include
from . import views
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView


# Для входа через Google
class GoogleLogin(OAuth2LoginView):
    adapter_class = GoogleOAuth2Adapter


urlpatterns = [
    path('', views.sign_view, name='sign_home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Правильный путь для Google OAuth
    path('google/login/', GoogleLogin.as_view(), name='google_login'),

    # Для allauth - используйте встроенные URLs
    path('accounts/', include('allauth.urls')),
    path('socialaccounts/', include('allauth.socialaccount.urls')),
]