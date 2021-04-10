from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError

from PIL import Image
from django.utils import timezone

UserModel = get_user_model()


class GenreForm(ModelForm):
    MIN_RESOLUTION = (400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Загружайте изображения с минимальным разрешением {}x{}'.format(
            *self.MIN_RESOLUTION)

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_height, min_width = self.MIN_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise ValidationError(
                f'Ваше изображение с разрешением {img.height}x{img.width} не удовлетворила требованиям')
        return image


class Genre(models.Model):
    form = GenreForm

    name = models.CharField(max_length=100, verbose_name='Название жанра')
    books_amount = models.IntegerField(verbose_name='Количество книг жанра')
    desc = models.TextField(verbose_name='Описание жанра', null=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='ФИО автора')
    books_amount = models.IntegerField(verbose_name='Количество книг автора')
    desc = models.TextField(verbose_name='Описание автора', null=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=100, verbose_name='Заголовок книги')
    author = models.ForeignKey(Author, verbose_name='Автор', on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, verbose_name='Жанр', on_delete=models.CASCADE)
    collateral_price = models.DecimalField(verbose_name='Залоговая стоимость', max_digits=9, decimal_places=2)
    rental_price = models.DecimalField(verbose_name='Стоимость проката', max_digits=9, decimal_places=2)
    amount = models.IntegerField(verbose_name='Количество книг')
    desc = models.TextField(verbose_name='Описание книги', null=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField()

    def __str__(self):
        return self.name


class ClientGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    discount = models.IntegerField(verbose_name='Скидка')
    clients_amount = models.IntegerField(verbose_name='Количество клиентов')
    show_prices = models.BooleanField(verbose_name='Показывать ли цены', default=True)
    status = models.BooleanField(verbose_name='Статус', default=True)

    def __str__(self):
        return self.name


class Client(AbstractBaseUser):
    # user = models.ForeignKey(User, verbose_name='Клиент', on_delete=models.CASCADE, null=True)
    # user = models.ForeignKey(AUTH_USER_MODEL, verbose_name='Клиент', on_delete=models.CASCADE)
    username = models.CharField(blank=True, max_length=150)
    email = models.EmailField(verbose_name='Адрес E-mail', max_length=150, unique=True)
    # help_text='Для регистрации укажите пожалуйста свой адрес электронной почты (E-mail)')

    first_name = models.CharField(verbose_name='Имя', max_length=70)
    last_name = models.CharField(verbose_name='Фамилия', max_length=70)

    date_of_birth = models.DateField(verbose_name='Дата рождения', blank=True, null=True)

    address = models.CharField(max_length=255, verbose_name='Адрес')
    mobile_phone = models.CharField(max_length=28, verbose_name='Мобильный номер', unique=True)
    home_phone = models.CharField(max_length=28, verbose_name='Домашний номер', unique=True, blank=True, null=True)
    group = models.ForeignKey(ClientGroup, on_delete=models.CASCADE, verbose_name='Группа', null=True)
    password = models.CharField(verbose_name='Пароль', max_length=128)
    is_active = models.BooleanField(verbose_name='Активен', default=False)
    last_login = models.DateTimeField(verbose_name='Дата и время последнего входа', null=True)
    register_datetime = models.DateTimeField(verbose_name='Дата и время регистрации', default=timezone.now)

    # EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'Клиент {self.first_name} {self.last_name}'

    class Meta(AbstractUser.Meta):
        swappable = 'mainapp.models.Client'


class Status(models.IntegerChoices):
    IN_PROCESS = 1
    ABANDONED = 2
    CLOSED = 3
    ON_HANDS = 4
    EXPIRED = 5


class Basket(models.Model):
    books = models.ManyToManyField(Book, blank=True, verbose_name='Книги в корзине')
    status = models.IntegerField(choices=Status.choices, verbose_name='Статус')
    client = models.ForeignKey(AUTH_USER_MODEL, verbose_name='Клиент', on_delete=models.CASCADE)
    return_date = models.DateTimeField(verbose_name='Дата и время возврата')
    date_of_taking = models.DateTimeField(verbose_name='Дата и время взятия')

    def __str__(self):
        return f'Корзина клиента {self.client} от {self.date_of_taking}'
