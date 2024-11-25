from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django_ratelimit.decorators import ratelimit

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User, Consulta, Prontuario
from .serializers import UserSerializer, ConsultaSerializer, ProntuarioSerializer

from .utils import gerar_horarios_disponiveis, filtrar_horarios_ocupados

import json
from datetime import datetime
from collections import Counter
import logging

logger = logging.getLogger(__name__)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def get_users(request):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET','PUT'])
def get_by_cpf(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        user = User.objects.get(pk=cpf)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)   
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def user_manager(request):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    if request.method == 'GET':
        try:
            if request.GET['user']:                     
                user_cpf = request.GET['user'] 
                try:
                    user = User.objects.get(pk=user_cpf) 
                except:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                serializer = UserSerializer(user)          
                return Response(serializer.data)       

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'POST':
        new_user = request.data
        serializer = UserSerializer(data=new_user)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PUT':
        user_cpf = request.data['user_cpf'] 
        try:
            user_to_update = User.objects.get(pk=user_cpf) 
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user_to_update, data=request.data)   
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
    if request.method == 'DELETE':
        try:
            user_to_delete = User.objects.get(pk=request.data['user_cpf'])
            user_to_delete.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['POST'])
def register_user(request):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['user_password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['POST'])
def login_user(request):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    if request.method == 'POST':
        cpf = request.data.get('user_cpf')
        password = request.data.get('user_password')
        try:
            user = User.objects.get(user_cpf=cpf)
            if user.check_password(password):
                return Response({"message": "Login bem-sucedido", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Senha incorreta"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['POST'])
def marcar_consulta(request):
    if getattr(request, 'limited', False):
        logger.warning("Usuário bloqueado por excesso de requisições: IP=%s", get_client_ip(request))
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        consulta_data = request.data
        serializer = ConsultaSerializer(data=consulta_data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Consulta agendada com sucesso: %s", consulta_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.warning("Erro na validação dos dados: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Erro ao processar a solicitação de agendamento")
        return Response(
            {"error": "Erro interno ao processar a solicitação."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def listar_consultas_paciente(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        consultas = Consulta.objects.filter(paciente__user_cpf=cpf)
        serializer = ConsultaSerializer(consultas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def horarios_disponiveis(request, cpf, data):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        data = datetime.strptime(data, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {"error": "O parâmetro 'data' deve estar no formato 'YYYY-MM-DD'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if data == timezone.now().date():
        current_time = timezone.now().time()
        if current_time < datetime.strptime('12:00', '%H:%M').time():
            horarios_disponiveis = gerar_horarios_disponiveis(data)
            horarios_disponiveis = [
                horario for horario in horarios_disponiveis 
                if horario.time() >= datetime.strptime('14:00', '%H:%M').time()
            ]
        else:
            return Response(
                {"error": "Não há horários disponíveis para hoje à tarde."},
                status=status.HTTP_204_NO_CONTENT
            )
    else:
        try:
            medico = User.objects.get(user_cpf=cpf, user_type='doctor')
        except User.DoesNotExist:
            return Response(
                {"error": "Médico com o CPF fornecido não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        horarios_disponiveis = gerar_horarios_disponiveis(data)

    horarios_filtrados = filtrar_horarios_ocupados(horarios_disponiveis, medico, data)

    return Response({"horarios_disponiveis": horarios_filtrados}, status=status.HTTP_200_OK)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def listar_medicos(request):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        medicos = User.objects.filter(user_type='doctor')  
        serializer = UserSerializer(medicos, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def listar_consultas_medico(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        medico = User.objects.get(user_cpf=cpf, user_type='doctor') 
        consultas = Consulta.objects.filter(medico=medico)  
        serializer = ConsultaSerializer(consultas, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Médico não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['PUT'])
def atualizar_status_consulta(request, consulta_id):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        consulta = Consulta.objects.get(id=consulta_id)  
    except Consulta.DoesNotExist:
        return Response({"error": "Consulta não encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    novo_status = request.data.get('status')
    
    if novo_status not in dict(Consulta.STATUS_CHOICES).keys():
        return Response({"error": "Status inválido."}, status=status.HTTP_400_BAD_REQUEST)
    
    consulta.status = novo_status
    consulta.save()
    
    serializer = ConsultaSerializer(consulta)
    return Response(serializer.data, status=status.HTTP_200_OK)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def listar_consultas_hoje_medico(request, cpf):
    if getattr(request, 'limited', False):
        logger.warning(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        medico = User.objects.get(user_cpf=cpf, user_type='doctor')
        data_atual = timezone.now().date()
        consultas = Consulta.objects.filter(medico=medico, data_hora__date=data_atual)
        serializer = ConsultaSerializer(consultas, many=True)
        
        logger.info(f"Consultas listadas para médico CPF: {cpf}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        logger.error(f"User with CPF {cpf} not found or not a doctor.")
        return Response({"error": "Médico não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("An unexpected error occurred while listing consultas.")
        return Response({"error": "Erro interno no servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def consultas_por_dia(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        medico = User.objects.get(user_cpf=cpf, user_type='doctor')
        hoje = timezone.now().date()
        fim_periodo = hoje + timezone.timedelta(days=6)

        consultas = Consulta.objects.filter(
            medico=medico, 
            data_hora__date__range=[hoje, fim_periodo]
        )

        resultado = {}
        for dia in range(7):
            data = hoje + timezone.timedelta(days=dia)
            count = consultas.filter(data_hora__date=data).count()
            resultado[str(data)] = count

        return Response({"consultas_por_dia": resultado}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Médico não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def horarios_mais_requisitados(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        medico = User.objects.get(user_cpf=cpf, user_type='doctor')
        consultas = Consulta.objects.filter(medico=medico)
        
        horarios = [consulta.data_hora.time() for consulta in consultas]
        contagem_horarios = Counter(horarios)
        horarios_ordenados = contagem_horarios.most_common()

        return Response({"horarios_mais_requisitados": horarios_ordenados}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Médico não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def contagem_por_status(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        medico = User.objects.get(user_cpf=cpf, user_type='doctor')
        consultas = Consulta.objects.filter(medico=medico)
        
        status_contagem = consultas.values('status').annotate(total=Count('status'))

        return Response({"contagem_por_status": list(status_contagem)}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Médico não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['POST'])
def criar_prontuario(request):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    serializer = ProntuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def prontuarios_por_paciente(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    prontuarios = Prontuario.objects.filter(cpf=cpf)
    prontuarios_data = list(prontuarios.values()) 
    return JsonResponse(prontuarios_data, safe=False)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def prontuarios_por_medico(request, medico_cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    prontuarios = Prontuario.objects.filter(medico_cpf=medico_cpf)
    prontuarios_data = list(prontuarios.values())  
    return JsonResponse(prontuarios_data, safe=False)

@ratelimit(key='ip', rate='10/m', block=False)
@api_view(['GET'])
def ultima_anamnese_por_cpf(request, cpf):
    if getattr(request, 'limited', False):
        return Response(
            {"error": "Limite de requisições excedido. Tente novamente mais tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    try:
        ultimo_prontuario = Prontuario.objects.filter(cpf=cpf).order_by('-id').first()
        if ultimo_prontuario is None:
            return JsonResponse({"error": "O paciente não tem prontuários anteriores."}, status=404)
        anamnese_data = {
            "nome": ultimo_prontuario.nome,
            "cpf": ultimo_prontuario.cpf,
            "queixa_principal": ultimo_prontuario.queixa_principal,
            "historia_doenca_atual": ultimo_prontuario.historia_doenca_atual,
            "antecedentes_pessoais_fisiologicos": ultimo_prontuario.antecedentes_pessoais_fisiologicos,
            "antecedentes_pessoais_patologicos": ultimo_prontuario.antecedentes_pessoais_patologicos,
            "antecedentes_familiares": ultimo_prontuario.antecedentes_familiares,
            "habitos_condicoes_vida": ultimo_prontuario.habitos_condicoes_vida,
        }
        
        return JsonResponse(anamnese_data)
    
    except ObjectDoesNotExist:
        return JsonResponse({"error": "O paciente não tem prontuários anteriores."}, status=404)