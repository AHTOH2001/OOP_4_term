from django.contrib.auth.hashers import make_password
from datetime import datetime
from .models import Client, ClientGroup


def get_code(obj, seed, length=40):
    return make_password(obj, seed)[-length:]


def should_show_price(user):
    if is_administrator(user):
        group, is_created = ClientGroup.objects.get_or_create(name='Гость')
        return group.show_prices
    else:
        client = user.client_set.get()
        return client.group.show_prices


def is_administrator(user):
    try:
        user.client_set.get()
    except Client.DoesNotExist:
        return True
    else:
        return False
