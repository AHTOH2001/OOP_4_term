from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone
from django.contrib.auth import login, logout
from django import urls

# from django.contrib.auth.hashers import make_password, check_password, is_password_usable

# from datetime import datetime
from CheekLit import settings
from .utils import get_code
from .models import Client
from .forms import ClientRegisterForm, ClientAuthorizationForm
from .settings import time_for_registration


def home(request):
    return render(request, 'home.html', {})


def register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(data=request.POST)
        if form.is_valid():
            client = form.save()

            confirmation_url = request.META["HTTP_HOST"] + urls.reverse(
                register_complete) + f'?login={client.email}&code={get_code(client.email, "abs", 20)}'
            email_message = f'''Здравствуйте, уважаемый {client.last_name} {client.first_name}!

Вы в одном шаге от завершения регистрации в интернет библиотеке CheekLit.

Ваши данные для авторизации в системе:

Логин: {client.email}
Пароль: {client.password}

Внимание! Вы должны подтвердить регистрационные данные!
Для подтверждения достаточно перейти по следующей ссылке:

{confirmation_url}

Если Вы действительно желаете подтвердить регистрацию, пожалуйста, сделайте это до {(timezone.now() + time_for_registration).strftime('%H:%M %d.%m.%Y')}. В противном случае Ваши регистрационные данные будут удалены из системы.

С уважением, администрация интернет библиотеки CheekLit'''

            send_mail(
                f'Подтверждение регистрации на сайте {request.META["HTTP_HOST"]}',
                email_message,
                'CheekLitBot@gmail.com',
                [client.email],
                fail_silently=False,
            )
            messages.success(request, 'Пользователь успешно создан, проверьте почту и подтвердите регистрацию')
            return redirect('home')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = ClientRegisterForm()
    return render(request, 'register.html', {'form': form})


def register_complete(request):
    try:
        email = request.GET['login']
        code = request.GET['code'].replace(' ', '+')
        if get_code(email, 'abs', 20) == code:
            # Delete outdated clients
            Client.objects.filter(register_datetime__lt=timezone.now() - time_for_registration,
                                  is_active=False).delete()
            try:
                if Client.objects.get(email=email).is_active is True:
                    messages.warning(request, 'Пользователь уже подтверждён')
                else:
                    messages.success(request, 'Пользователь успешно подтверждён, осталось только авторизоваться')
                    Client.objects.filter(email=email).update(is_active=True)
                    return redirect('authorize')
            except Client.DoesNotExist:
                messages.error(request, 'По всей видимости ссылка регистрации просрочена')
        else:
            messages.error(request, f'Параметр code неверный')

    except MultiValueDictKeyError as e:
        messages.error(request, f'Пропущен параметр {e.args}')

    return redirect('home')


def authorize(request):
    if request.method == 'POST':
        form = ClientAuthorizationForm(data=request.POST)
        if form.is_valid():
            client = form.get_user()
            login(request, client)
            messages.success(request, f'Добро пожаловать, {client.last_name} {client.first_name}')
            return redirect('home')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = ClientAuthorizationForm()
    return render(request, 'authorize.html', {'form': form})


def client_logout(request):
    logout(request)
    return redirect('home')
