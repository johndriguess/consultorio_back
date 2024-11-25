from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Consulta
from .models import User
from rest_framework.test import APIClient
import logging
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
logger = logging.getLogger('django')

class ListarConsultasHojeMedicoTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.medico = User.objects.create(
            user_name="Dr. João",
            user_cpf="12345678900",
            user_password="senha123",
            user_email="dr.joao@example.com",
            user_data_nasc="1970-01-01",
            user_type="doctor",
            user_genero="masculino",
            user_telefone="123456789",
            doctor_especialidade="Cardiologista",
            doctor_crm="CRM12345"
        )

        self.paciente1 = User.objects.create(
            user_name="Ana",
            user_cpf="11111111111",
            user_password="senha123",
            user_email="ana@example.com",
            user_data_nasc="1990-01-01",
            user_type="paciente",
            user_genero="feminino",
            user_telefone="987654321"
        )
        
        self.paciente2 = User.objects.create(
            user_name="Carlos",
            user_cpf="22222222222",
            user_password="senha123",
            user_email="carlos@example.com",
            user_data_nasc="1985-01-01",
            user_type="paciente",
            user_genero="masculino",
            user_telefone="123123123"
        )

        self.consulta_hoje1 = Consulta.objects.create(
            paciente=self.paciente1,
            medico=self.medico,
            data_hora=timezone.now(),
            status="marcada",
            motivo="Dor no peito"
        )

        self.consulta_hoje2 = Consulta.objects.create(
            paciente=self.paciente2,
            medico=self.medico,
            data_hora=timezone.now(),
            status="marcada",
            motivo="Hipertensão"
        )

        self.consulta_ontem = Consulta.objects.create(
            paciente=self.paciente1,
            medico=self.medico,
            data_hora=timezone.now() - timezone.timedelta(days=1),
            status="marcada",
            motivo="Dor de cabeça"
        )

        self.outro_medico = User.objects.create(
            user_name="Dr. Marcos",
            user_cpf="99999999999",
            user_password="senha123",
            user_email="dr.marcos@example.com",
            user_data_nasc="1980-01-01",
            user_type="doctor",
            user_genero="masculino",
            user_telefone="456456456",
            doctor_especialidade="Neurologista",
            doctor_crm="CRM54321"
        )

        self.consulta_outro_medico = Consulta.objects.create(
            paciente=self.paciente1,
            medico=self.outro_medico,
            data_hora=timezone.now(),
            status="marcada",
            motivo="Tontura"
        )

    def test_listar_consultas_hoje_medico(self):
        """Testa se as consultas do dia atual para o médico especificado são listadas corretamente."""
        response = self.client.get(reverse('listar_consultas_hoje_medico', args=[self.medico.user_cpf]))
        self.assertEqual(response.status_code, 200)

        consultas = response.json()
        self.assertEqual(len(consultas), 2)  
        self.assertEqual(consultas[0]['motivo'], "Dor no peito")
        self.assertEqual(consultas[1]['motivo'], "Hipertensão")


class MetricaQualidadeTentativasDeLogin(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.medico = User.objects.create(
            user_name='testuser',
            user_cpf='12345678901',
            user_email='testuser@example.com',
            user_data_nasc='1980-01-01',
            user_type='doctor',
            user_genero='M',
            user_telefone='123456789',
            doctor_especialidade='Cardiologia',
            doctor_crm='1234567'
        )
        self.medico.set_password('password123')
        self.medico.save()

    def test_calculate_login_success_rate(self):
        successful_logins = 0
        failed_logins = 0

        for _ in range(3):
            response = self.client.post(reverse('login_user'), {
                'user_cpf': '12345678901',
                'user_password': 'password123',
            })
            if response.status_code == 200:
                successful_logins += 1

        for _ in range(2):
            response = self.client.post(reverse('login_user'), {
                'user_cpf': '12345678901',
                'user_password': 'wrongpassword',
            })
            if response.status_code != 200:
                failed_logins += 1

        total_attempts = successful_logins + failed_logins
        success_rate = (successful_logins / total_attempts) * 100 if total_attempts > 0 else 0

        self.assertEqual(successful_logins, 3)
        self.assertEqual(failed_logins, 2)
        self.assertEqual(success_rate, 60)

from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


class MetricaTaxaSucessoAutenticacao(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Criar um usuário válido
        self.medico = User.objects.create(
            user_name='medico_teste',
            user_cpf='98765432100',
            user_email='medico_teste@example.com',
            user_data_nasc='1975-12-01',
            user_type='doctor',
            user_genero='M',
            user_telefone='987654321',
            doctor_especialidade='Ortopedia',
            doctor_crm='3214567'
        )
        self.medico.set_password('senha_correta')
        self.medico.save()

    def test_forca_bruta_bloqueada(self):
        """Testa se o sistema bloqueia tentativas de login por força bruta com limitação de requisições."""
        limite_tentativas = 10  # O rate limit permite 10 requisições por minuto
        tentativas_falhas = 0
        bloqueios = 0

        for i in range(limite_tentativas + 5):  # Testar além do limite
            response = self.client.post(reverse('login_user'), {
                'user_cpf': '98765432100',
                'user_password': 'senha_errada',
            })

            if response.status_code == HTTP_400_BAD_REQUEST:
                tentativas_falhas += 1
            elif response.status_code == HTTP_429_TOO_MANY_REQUESTS:
                bloqueios += 1

        # Validar que o número de tentativas falhas é menor ou igual ao limite
        self.assertLessEqual(tentativas_falhas, limite_tentativas)
        # Verificar que houve pelo menos um bloqueio
        self.assertGreaterEqual(bloqueios, 1)

    def test_login_bloqueado_apos_rate_limit(self):
        """Testa se o sistema bloqueia corretamente após exceder o limite de requisições."""
        for i in range(10):  # Fazer 10 requisições inválidas no limite permitido
            response = self.client.post(reverse('login_user'), {
                'user_cpf': '98765432100',
                'user_password': 'senha_errada',
            })
            if response.status_code == HTTP_429_TOO_MANY_REQUESTS:
                break
            self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Verificar que a próxima requisição é bloqueada
        response = self.client.post(reverse('login_user'), {
            'user_cpf': '98765432100',
            'user_password': 'senha_errada',
        })
        self.assertEqual(response.status_code, HTTP_429_TOO_MANY_REQUESTS)

    def test_login_sucesso_apos_rate_limit(self):
        """Testa se o login bem-sucedido é permitido após o limite ser alcançado."""
        for i in range(10):  # Fazer 10 requisições inválidas no limite permitido
            response = self.client.post(reverse('login_user'), {
                'user_cpf': '98765432100',
                'user_password': 'senha_errada',
            })
            if response.status_code == HTTP_429_TOO_MANY_REQUESTS:
                break
            self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Atingir o limite, a próxima requisição será bloqueada
        response = self.client.post(reverse('login_user'), {
            'user_cpf': '98765432100',
            'user_password': 'senha_errada',
        })
        self.assertEqual(response.status_code, HTTP_429_TOO_MANY_REQUESTS)

        # Esperar o período de rate limit (ajuste necessário para testes reais)
        import time
        time.sleep(61)  # Simular a expiração do limite (tempo baseado na configuração)

        # Tentar novamente com credenciais corretas
        response = self.client.post(reverse('login_user'), {
            'user_cpf': '98765432100',
            'user_password': 'senha_correta',
        })
        self.assertEqual(response.status_code, HTTP_200_OK)