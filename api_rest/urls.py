from . import views
from django.urls import path

urlpatterns = [
    path('users', views.get_users, name='get_all_users'),
    path('users/<str:cpf>', views.get_by_cpf),
    path('data/', views.user_manager),
    path('register/', views.register_user, name='register_user'),  
    path('login/', views.login_user, name='login_user'),  
]
