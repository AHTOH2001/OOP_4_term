from django import template

from mainapp.models import Client, ClientGroup, Status, Basket

register = template.Library()


@register.simple_tag
def get_field_name(model, field_name):
    for fld in model._meta.fields:
        if fld.name == field_name:
            return fld.verbose_name
    raise KeyError(f"model {model} doesn't have field {field_name}")


@register.filter
def should_show_price(user):
    if is_administrator(user):
        return True
    elif not user.is_authenticated:
        return ClientGroup.objects.get_or_create(name='Не авторизованный')[0].show_prices
    else:
        client = user.client_set.get()
        return client.group.show_prices


@register.filter
def is_administrator(user):
    if not user.is_authenticated:
        return False
    try:
        user.client_set.get()
    except Client.DoesNotExist:
        return True
    else:
        return False


@register.filter
def calculate_price(price, user):
    if is_administrator(user):
        return price
    else:
        try:
            client = user.client_set.get()
            group = client.group
        except AttributeError:
            group, is_created = ClientGroup.objects.get_or_create(name='Не авторизованный')
        return round(price - price * group.discount / 100, 2)


@register.filter
def is_have_abandoned_basket(user):
    if is_administrator(user):
        return False
    else:
        client = user.client_set.get()
        try:
            client.baskets.get(status=Status.ABANDONED)
        except Basket.DoesNotExist:
            return False
        else:
            return True

#
# @register.simple_tag
# def get_shop_genres():
#     return Genre.objects.all()
#
#
# @register.simple_tag
# def get_shop_authors():
#     return Author.objects.all()
