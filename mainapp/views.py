from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone
from django.contrib.auth import login, logout
from django import urls
import copy

# from django.contrib.auth.hashers import make_password, check_password, is_password_usable

# from datetime import datetime
from django.views.generic import DetailView

from CheekLit import settings
from .utils import get_code, is_administrator, should_show_price
from .models import Client, Book, Author, Genre, Basket, Status, SliderImages
from .forms import ClientRegisterForm, ClientAuthorizationForm
from .settings import time_for_registration


def home(request):
    books = Book.objects.filter(status=True).order_by('-amount')
    slider_images = SliderImages.objects.filter(status=True)
    # return render(request, 'home.html', {'books': books, 'is_administrator': is_administrator(request.user)})
    return render(request, 'home.html',
                  {'books': books, 'genres': Genre.objects.all(), 'authors': Author.objects.all(),
                   'slider_images': slider_images})


def book_detail(request, slug):
    current_book = Book.objects.get(slug=slug)
    if request.method == 'POST':
        if 'add_to_basket' in request.GET:
            if is_administrator(request.user):
                raise Http404('Administration does not have a basket')
            client = request.user.client_set.get()
            current_basket, is_created = client.baskets.get_or_create(status=Status.IN_PROCESS)
            if should_show_price(request.user):
                current_basket.books.add(current_book)
                messages.success(request, 'Книга успешно добавлена в корзину')
    return render(request, 'book_detail.html', {'book': current_book})
    # return super(BookDetailView, self).get(request, *args, **kwargs)


# class BookDetailView(DetailView):
#     queryset = Book.objects.all()
#     model = Book
#     context_object_name = 'book'
#     template_name = 'book_detail.html'
#     slug_url_kwarg = 'slug'
#
#     def post(self, request, *args, **kwargs):
#         pass
#         # context = super().get_context_data(object=self.object)
#         # return super().render_to_response(context)


class AuthorDetailView(DetailView):
    queryset = Author.objects.all()
    model = Author
    context_object_name = 'author'
    template_name = 'author_detail.html'
    slug_url_kwarg = 'slug'


class GenreDetailView(DetailView):
    queryset = Genre.objects.all()
    model = Genre
    context_object_name = 'genre'
    template_name = 'genre_detail.html'
    slug_url_kwarg = 'slug'


def register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(data=request.POST)
        if form.is_valid():
            client, raw_pass = form.save()

            confirmation_url = request.META["HTTP_HOST"] + urls.reverse(
                register_complete) + f'?login={client.user.email}&code={get_code(client.user.email, "abs", 20)}'
            email_message = f'''Здравствуйте, уважаемый {client.user.last_name} {client.user.first_name}!

Вы в одном шаге от завершения регистрации в интернет библиотеке CheekLit.

Ваши данные для авторизации в системе:

Логин: {client.user.email}
Пароль: {raw_pass}

Внимание! Вы должны подтвердить регистрационные данные!
Для подтверждения достаточно перейти по следующей ссылке:

{confirmation_url}

Если Вы действительно желаете подтвердить регистрацию, пожалуйста, сделайте это до {(timezone.localtime() + time_for_registration).strftime('%H:%M %d.%m.%Y')}. В противном случае Ваши регистрационные данные будут удалены из системы.

С уважением, администрация интернет библиотеки CheekLit'''

            send_mail(
                f'Подтверждение регистрации на сайте {request.META["HTTP_HOST"]}',
                email_message,
                'CheekLitBot@gmail.com',
                [client.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Пользователь успешно создан, проверьте почту и подтвердите регистрацию')
            return redirect('home')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = ClientRegisterForm()
    return render(request, 'register.html',
                  {'form': form, 'genres': Genre.objects.all(), 'authors': Author.objects.all()})


def register_complete(request):
    try:
        email = request.GET['login']
        code = request.GET['code'].replace(' ', '+')
        if get_code(email, 'abs', 20) == code:
            # Delete outdated clients
            User.objects.filter(date_joined__lt=timezone.localtime() - time_for_registration,
                                is_active=False, is_staff=False, is_superuser=False).delete()
            try:
                if User.objects.get(email=email).is_active is True:
                    messages.warning(request, 'Пользователь уже подтверждён')
                else:
                    messages.success(request, 'Пользователь успешно подтверждён, осталось только авторизоваться')
                    User.objects.filter(email=email).update(is_active=True)
                    return redirect('authorize')
            except User.DoesNotExist:
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
    return render(request, 'authorize.html',
                  {'form': form, 'genres': Genre.objects.all(), 'authors': Author.objects.all()})


def client_logout(request):
    logout(request)
    return redirect('home')


def useful_information(request):
    return render(request, 'useful_information.html')


def about_us(request):
    return render(request, 'about_us.html')


def contact(request):
    return render(request, 'contact.html')


def basket(request):
    if request.user.is_authenticated:
        if is_administrator(request.user):
            raise Http404('Administration does not have a basket')

        client = request.user.client_set.get()
        current_basket, is_created = client.baskets.get_or_create(status=Status.IN_PROCESS)

        if not should_show_price(request.user):
            current_basket.books.clear()

        if request.method == 'POST':
            if 'delete_book' in request.GET:
                current_basket.books.remove(request.GET['delete_book'])
            if 'clear' in request.GET:
                saved_basket = copy.copy(current_basket)
                saved_basket.status = Status.ABANDONED
                Basket.objects.filter(client=client, status=Status.ABANDONED).delete()
                saved_basket.save()
                client.baskets.add(saved_basket)
                current_basket.books.clear()
                # client.baskets.create(status=Status.ABANDONED, )
            if 'restore' in request.GET:
                try:
                    client.baskets.get(status=Status.ABANDONED)
                except Basket.DoesNotExist:
                    raise Http404('Not found abandoned basket')
                client.baskets.filter(status=Status.IN_PROCESS).delete()
                client.baskets.filter(status=Status.ABANDONED).update(status=Status.IN_PROCESS)
                current_basket = client.baskets.get(status=Status.IN_PROCESS)
        return render(request, 'basket.html', {'BookModel': Book, 'books_in_basket': current_basket.books.all()})
    else:
        raise Http404('User is not authenticated')


def order(request):
    if request.user.is_authenticated and should_show_price(request.user):
        if is_administrator(request.user):
            raise Http404('Administration does not have a basket')

        client = request.user.client_set.get()
        current_basket, is_created = client.baskets.get_or_create(status=Status.IN_PROCESS)
        current_basket.status = Status.ON_HANDS
        current_basket.date_of_taking = timezone.now()
        current_basket.save()
        return render(request, 'order.html')
    else:
        raise Http404('User is not authenticated')
