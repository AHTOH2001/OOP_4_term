from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(ClientGroup)
admin.site.register(Client)
admin.site.register(Basket)
admin.site.register(SliderImages)

