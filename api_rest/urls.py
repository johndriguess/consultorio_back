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
    path('consultas/<int:consulta_id>/atualizar-status/', views.atualizar_status_consulta, name='atualizar_status_consulta'),
    path('consultas/hoje/<str:cpf>/', views.listar_consultas_hoje_medico, name='listar_consultas_hoje_medico'),
    path('consultas/proximos7dias/<str:cpf>/', views.consultas_por_dia, name='consultas_por_dia'),
    path('consultas/horarios-mais-requisitados/<str:cpf>/', views.horarios_mais_requisitados, name='horarios_mais_requisitados'),
    path('consultas/status-contagem/<str:cpf>/', views.contagem_por_status, name='contagem_por_status'),

]
