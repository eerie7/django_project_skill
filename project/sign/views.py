from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from News_portal.models import Author

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'

def logout_view(request):
    logout(request)
    return redirect('sign_home')

def sign_view(request):
    return render(request, 'sign/home.html')

# ДОБАВЬТЕ ЭТУ ФУНКЦИЮ ↓
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('sign_home')
    else:
        form = AuthenticationForm()
    return render(request, 'sign/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'sign/signup.html', {'form': form})


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')

    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
        # Профиль автора создастся автоматически через сигнал

    return redirect('/sign/')