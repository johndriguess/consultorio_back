from . import views
from django.urls import path

urlpatterns = [
    path('users', views.get_users, name='get_all_users'),
    path('users/<str:cpf>', views.get_by_cpf),
    path('data/', views.user_manager),
    path('register/', views.register_user, name='register_user'),  
    path('login/', views.login_user, name='login_user'),  
    path('consultas/marcar/', views.marcar_consulta, name='marcar_consulta'),
    path('consultas/paciente/<str:cpf>/', views.listar_consultas_paciente, name='listar_consultas_paciente'),
    path('consultas/horarios/<str:cpf>/<str:data>/', views.horarios_disponiveis, name='horarios_disponiveis'),
    path('users/medicos/', views.listar_medicos, name='listar_medicos'),  
    path('consultas/medico/<str:cpf>/', views.listar_consultas_medico, name='listar_consultas_medico'),
]
