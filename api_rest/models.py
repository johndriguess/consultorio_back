from django.db import models

class User(models.Model):
    user_name = models.CharField(max_length=100, default='')
    user_cpf = models.CharField(max_length=100, primary_key=True, default='')
    user_email = models.EmailField(default='')
    user_age = models.IntegerField(default=0)

    def __str__(self):
        return f'Name: {self.user_name} | Email: {self.user_email}'
