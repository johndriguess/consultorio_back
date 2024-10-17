from datetime import datetime, timedelta
from .models import Consulta
from django.utils.timezone import make_aware

def gerar_horarios_disponiveis(data):
    horario_manha_inicio = datetime.combine(data, datetime.strptime('08:00', '%H:%M').time())
    horario_manha_fim = datetime.combine(data, datetime.strptime('12:00', '%H:%M').time())
    
    horario_tarde_inicio = datetime.combine(data, datetime.strptime('14:00', '%H:%M').time())
    horario_tarde_fim = datetime.combine(data, datetime.strptime('18:00', '%H:%M').time())
    
    intervalo = timedelta(minutes=30)
    horarios_disponiveis = []
    
    while horario_manha_inicio < horario_manha_fim:
        horarios_disponiveis.append(horario_manha_inicio)
        horario_manha_inicio += intervalo
    
    while horario_tarde_inicio < horario_tarde_fim:
        horarios_disponiveis.append(horario_tarde_inicio)
        horario_tarde_inicio += intervalo

    return horarios_disponiveis

def filtrar_horarios_ocupados(horarios_disponiveis, medico, data):
    consultas_no_dia = Consulta.objects.filter(
        medico=medico,
        data_hora__date=data
    )

    horarios_ocupados = [consulta.data_hora for consulta in consultas_no_dia]
    horarios_disponiveis = [horario for horario in horarios_disponiveis if make_aware(horario) not in horarios_ocupados]
    
    return horarios_disponiveis
