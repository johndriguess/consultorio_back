from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('users', views.get_users, name='get_all_users'),
    path('users/<str:cpf>', views.get_by_cpf),
    path('data/', views.user_manager),
]