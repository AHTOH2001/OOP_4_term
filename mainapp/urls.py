from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('book/<str:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<str:slug>/', views.book_detail, name='book_detail'),
    path('author/<str:slug>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('genre/<str:slug>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('register/', views.register, name='register'),
    path('register/complete/', views.register_complete, name='register_complete'),
    path('authorize/', views.authorize, name='authorize'),
    path('logout/', views.client_logout, name='logout'),
    path('useful-information/', views.useful_information, name='useful_information'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('basket/', views.basket, name='basket'),
    path('order/', views.order, name='order')
]
