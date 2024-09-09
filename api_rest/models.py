from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    user_name = models.CharField(max_length=100, default='')
    user_cpf = models.CharField(max_length=100, primary_key=True, default='')
    user_password = models.CharField(max_length=128)  # Campo para senha hasheada
    user_email = models.EmailField(default='')
    user_age = models.IntegerField(default=0)

    def __str__(self):
        return f'Name: {self.user_name} | Email: {self.user_email}'

    # Método para hashear a senha
    def set_password(self, raw_password):
        self.user_password = make_password(raw_password)

    # Método para verificar a senha hasheada
    def check_password(self, raw_password):
        return check_password(raw_password, self.user_password)
