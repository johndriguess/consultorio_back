from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import check_password

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers import UserSerializer

import json

@api_view(['GET'])
def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT'])
def get_by_cpf(request, cpf):
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
    

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def user_manager(request):
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
    
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['user_password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login_user(request):
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