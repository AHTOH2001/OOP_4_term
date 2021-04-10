from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register/complete/', views.register_complete, name='register_complete'),
    path('authorize/', views.authorize, name='authorize'),
    path('logout/', views.client_logout, name='logout'),
]
