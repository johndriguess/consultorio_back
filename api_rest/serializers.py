from rest_framework import serializers
from .models import User, Consulta, Prontuario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.user_type == 'paciente':
            representation.pop('doctor_crm', None)
            representation.pop('doctor_especialidade', None)
        
        return representation
    
class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = [
            'id', 'paciente', 'medico', 'data_hora', 'status', 'motivo',
            'nome_medico', 'especialidade_medico', 'nome_paciente'
        ]
        read_only_fields = ['nome_medico', 'especialidade_medico', 'nome_paciente']

class ProntuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prontuario
        fields = '__all__'