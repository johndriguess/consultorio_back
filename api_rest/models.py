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
        ('atrasada', 'Atrasada'),
    ]
    
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_paciente')
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultas_medico')
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='marcada')
    motivo = models.TextField()
    
    nome_medico = models.CharField(max_length=100, default="Indefinido")
    especialidade_medico = models.CharField(max_length=100, default="Indefinido")
    nome_paciente = models.CharField(max_length=100, default="Indefinido")

    def save(self, *args, **kwargs):
        self.nome_medico = self.medico.user_name
        self.especialidade_medico = self.medico.doctor_especialidade
        self.nome_paciente = self.paciente.user_name
        super().save(*args, **kwargs)  

    def __str__(self):
        return f'{self.paciente.user_name} com {self.medico.user_name} em {self.data_hora}'

class Prontuario(models.Model):
    # Informações do paciente
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14)
    
    # Dados da anamnese
    queixa_principal = models.TextField(blank=True)
    historia_doenca_atual = models.TextField(blank=True)
    antecedentes_pessoais_fisiologicos = models.TextField(blank=True)
    antecedentes_pessoais_patologicos = models.TextField(blank=True)
    antecedentes_familiares = models.TextField(blank=True)
    habitos_condicoes_vida = models.TextField(blank=True)
    
    # Dados SOAP
    subjetivo = models.TextField(blank=True)
    objetivo = models.TextField(blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    imc = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    pressao_arterial = models.CharField(max_length=20, blank=True)
    frequencia_respiratoria = models.CharField(max_length=20, blank=True)
    frequencia_cardiaca = models.CharField(max_length=20, blank=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    saturacao_o2 = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    vacina_em_dia = models.BooleanField(default=False)
    
    # Exames e Avaliação
    exames_solicitados = models.TextField(blank=True)
    avaliacao = models.TextField(blank=True)
    problema_condicao = models.TextField(blank=True)
    plano = models.TextField(blank=True)
    
    # Informações adicionais
    consulta = models.ForeignKey('Consulta', on_delete=models.CASCADE)
    medico_cpf = models.CharField(max_length=100)
    medico_nome = models.CharField(max_length=255)
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Prontuário de {self.nome} (CPF: {self.cpf})'