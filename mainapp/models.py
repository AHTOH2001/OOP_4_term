from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError

from PIL import Image
from django.urls import reverse
from django.utils import timezone
import pytils.translit
from .settings import default_collateral_price_less_than_rental_price_by as koef

UserModel = get_user_model()


class GenreForm(ModelForm):
    MIN_RESOLUTION = (400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = 'Загружайте изображения с минимальным разрешением {}x{}'.format(
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

    name = models.CharField(max_length=100, verbose_name='Название жанра', unique=True)
    books_amount = models.IntegerField(verbose_name='Количество книг жанра', editable=False, default=0)
    desc = models.TextField(verbose_name='Описание жанра', blank=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def clean_fields(self, exclude=None):
        if self.slug == '':
            self.slug = pytils.translit.translify(self.name).replace(' ', '-')
        super(Genre, self).clean_fields(exclude=exclude)

    def get_absolute_url(self):
        return reverse('genre_detail', kwargs={'slug': self.slug})


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='ФИО автора', unique=True)
    books_amount = models.IntegerField(verbose_name='Количество книг автора', editable=False, default=0)
    desc = models.TextField(verbose_name='Описание автора', blank=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(verbose_name='Изображение')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    # def clean_slug(self):
    #     raise Exception('clean_slug')
    #     pass

    def clean_fields(self, exclude=None):
        if self.slug == '':
            self.slug = pytils.translit.translify(self.name).replace(' ', '-')
        super(Author, self).clean_fields(exclude=exclude)

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'slug': self.slug})


# TODO add help text to fields in admin
class Book(models.Model):
    name = models.CharField(max_length=100, verbose_name='Заголовок книги', unique=True)
    author = models.ForeignKey(Author, verbose_name='Автор', on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, verbose_name='Жанр', on_delete=models.CASCADE)
    collateral_price = models.DecimalField(verbose_name='Залоговая стоимость', max_digits=9, decimal_places=2,
                                           blank=True)
    rental_price = models.DecimalField(verbose_name='Стоимость проката', max_digits=9, decimal_places=2)
    amount = models.IntegerField(verbose_name='Количество', default=0, blank=True)
    desc = models.TextField(verbose_name='Описание книги', blank=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(verbose_name='Изображение')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'slug': self.slug})

    def clean_fields(self, exclude=None):
        if self.slug == '':
            self.slug = pytils.translit.translify(self.name).replace(' ', '-')
        if self.collateral_price is None:
            self.collateral_price = round(self.rental_price / koef, 2)

        super(Book, self).clean_fields(exclude=exclude)


class ClientGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    discount = models.IntegerField(verbose_name='Скидка')
    clients_amount = models.IntegerField(verbose_name='Количество клиентов')
    show_prices = models.BooleanField(verbose_name='Показывать ли цены', default=True)
    status = models.BooleanField(verbose_name='Статус', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа клиентов'
        verbose_name_plural = 'Группы клиентов'


class Status(models.IntegerChoices):
    IN_PROCESS = 1
    ABANDONED = 2
    CLOSED = 3
    ON_HANDS = 4
    EXPIRED = 5


class Basket(models.Model):
    books = models.ManyToManyField(Book, blank=True, verbose_name='Книги в корзине')
    status = models.IntegerField(choices=Status.choices, verbose_name='Статус')
    # client = models.ForeignKey(AUTH_USER_MODEL, verbose_name='Клиент', on_delete=models.CASCADE)
    return_date = models.DateTimeField(verbose_name='Дата и время возврата', null=True)
    date_of_taking = models.DateTimeField(verbose_name='Дата и время взятия', null=True)

    def __str__(self):
        return f'Корзина клиента от {self.date_of_taking} с {len(self.books)} книгами'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Client(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name='Клиент', on_delete=models.CASCADE, null=True)

    date_of_birth = models.DateField(verbose_name='Дата рождения', blank=True, null=True)

    address = models.CharField(max_length=255, verbose_name='Адрес')
    mobile_phone = models.CharField(max_length=28, verbose_name='Мобильный номер', unique=True)
    home_phone = models.CharField(max_length=28, verbose_name='Домашний номер', unique=True, blank=True, null=True)
    group = models.ForeignKey(ClientGroup, on_delete=models.CASCADE, verbose_name='Группа', null=True)
    baskets = models.ManyToManyField(Basket, verbose_name='Корзины клиента')

    def __str__(self):
        # return f'{self.user.first_name} {self.last_name}'
        return str(self.user)

    class Meta(AbstractUser.Meta):
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def get_my_current_basket(self):
        basket = Basket.objects.get(client=self, status=Status.IN_PROCESS)
        return basket
