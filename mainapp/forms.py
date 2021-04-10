from django.contrib.auth import get_user_model, password_validation
# from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django import forms
from django.utils.text import capfirst
from django.core import validators
from django import urls
from django.utils.translation import gettext, gettext_lazy as _

from CheekLit import settings
import re
# from datetime import datetime, timedelta
from . import views
from .models import Client
from .settings import time_for_registration

from .utils import get_code

from django.core.exceptions import ValidationError
from django.core.mail import send_mail

UserModel = get_user_model()

BIRTH_YEAR_CHOICES = [str(year) for year in range(1921, 2022)]


class ClientRegisterForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('is_active', 'group', 'last_login', 'register_datetime', 'username')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.SelectDateWidget(attrs={'class': 'form-control'}, years=BIRTH_YEAR_CHOICES),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'home_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'email': 'Для регистрации укажите пожалуйста свой адрес электронной почты (E-mail)',
        }

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean_mobile_phone(self):
        phone = self.cleaned_data['mobile_phone']
        pattern = r'^\+?\(?[0-9]{1,4}\)?[-\s\./0-9]+$'
        if re.match(pattern, phone):
            return phone
        else:
            raise ValidationError('Неправильно введён мобильный номер (пример правильного: +375291234567)')

    def clean_home_phone(self):
        phone = self.cleaned_data['home_phone']
        if not phone:
            return phone
        pattern = r'^\+?\(?[0-9]{1,4}\)?[-\s\./0-9]+$'
        if re.match(pattern, phone):
            return phone
        else:
            raise ValidationError('Неправильно введён домашний номер (пример правильного: 80291234567)')

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                self.add_error('password', error)

    def as_div(self):
        "Return this form rendered as HTML <div>s."
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(field)s%(help_text)s</div><br>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )

    def save(self, request=None, commit=True):
        super().save(commit=commit)

        # user = User.objects.create_user(username=f'Клиент_{self.instance.id}',
        #                                 email=self.cleaned_data['email'],
        #                                 password=self.cleaned_data['password'],
        #                                 first_name=self.cleaned_data['first_name'],
        #                                 last_name=self.cleaned_data['last_name'],
        #                                 is_active=False)
        Client.objects.filter(email=self.cleaned_data['email']).update(username=self.cleaned_data['email'])

        return self.instance


# TODO забыли пароль
class ClientAuthorizationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
                                help_text='Для авторизации укажите пожалуйста свой адрес электронной почты (E-mail)',
                                label='E-mail')
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}),
        help_text='Пароль указанный при регистрации'
    )

    # class Meta:
    #     model = Client
    #     fields = ('email', 'password')

    # widgets = {
    #     'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
    #     'password': forms.PasswordInput(attrs={, 'autocomplete': 'current-password'})
    # }
    # help_texts = {
    #     'email': 'Для авторизации укажите пожалуйста свой адрес электронной почты (E-mail)',
    #     'password': 'Пароль указанный при регистрации',
    # }

    def as_div(self):
        "Return this form rendered as HTML <div>s."
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(field)s%(help_text)s</div><br>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )

    # TODO try del field username from client
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            try:
                self.user_cache = Client.objects.get(email=email, password=password)
            except Client.DoesNotExist:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
