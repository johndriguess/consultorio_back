from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    user_name = models.CharField(max_length=100)
    user_cpf = models.CharField(max_length=100, primary_key=True)
    user_password = models.CharField(max_length=128)  
    user_email = models.EmailField()
    user_data_nasc = models.CharField(max_length=100)
    user_type = models.CharField(max_length=100)
    user_genero = models.CharField(max_length=100)
    user_telefone = models.CharField(max_length=100)
    doctor_especialidade = models.CharField(max_length=100, default='')
    doctor_crm = models.CharField(max_length=100, default='')
    
    def __str__(self):
        return f'Name: {self.user_name} | Email: {self.user_email}'

    def set_password(self, raw_password):
        self.user_password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.user_password)
    
class Consulta(models.Model):
    STATUS_CHOICES = [
        ('marcada', 'Marcada'),
        ('cancelada', 'Cancelada'),
        ('concluída', 'Concluída'),
    ]
    
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_paciente')
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_medico')
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='marcada')
    motivo = models.TextField()

    def __str__(self):
        return f'{self.paciente.user_name} com {self.medico.user_name} em {self.data_hora}'
