from rest_framework import serializers
from .models import User, Consulta

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
        fields = '__all__'