from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('', include('News_portal.urls')),  # новости и подписки
    path('sign/', include('sign.urls')),    # личный кабинет
    path('accounts/', include('allauth.urls')),
]