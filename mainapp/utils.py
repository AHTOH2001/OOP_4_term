from django.contrib.auth.hashers import make_password
from datetime import datetime
from .models import Client


def get_code(obj, seed, length=40):
    return make_password(obj, seed)[-length:]
