# Generated by Django 5.1.1 on 2024-11-03 14:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0006_consulta_especialidade_medico_consulta_nome_medico_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consulta',
            name='status',
            field=models.CharField(choices=[('marcada', 'Marcada'), ('cancelada', 'Cancelada'), ('concluída', 'Concluída'), ('atrasada', 'Atrasada')], default='marcada', max_length=20),
        ),
        migrations.CreateModel(
            name='Prontuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('cpf', models.CharField(max_length=14)),
                ('queixa_principal', models.TextField(blank=True)),
                ('historia_doenca_atual', models.TextField(blank=True)),
                ('antecedentes_pessoais_fisiologicos', models.TextField(blank=True)),
                ('antecedentes_pessoais_patologicos', models.TextField(blank=True)),
                ('antecedentes_familiares', models.TextField(blank=True)),
                ('habitos_condicoes_vida', models.TextField(blank=True)),
                ('subjetivo', models.TextField(blank=True)),
                ('objetivo', models.TextField(blank=True)),
                ('peso', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('altura', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('imc', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('pressao_arterial', models.CharField(blank=True, max_length=20)),
                ('frequencia_respiratoria', models.CharField(blank=True, max_length=20)),
                ('frequencia_cardiaca', models.CharField(blank=True, max_length=20)),
                ('temperatura', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('saturacao_o2', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('vacina_em_dia', models.BooleanField(default=False)),
                ('exames_solicitados', models.TextField(blank=True)),
                ('avaliacao', models.TextField(blank=True)),
                ('problema_condicao', models.TextField(blank=True)),
                ('plano', models.TextField(blank=True)),
                ('medico_cpf', models.CharField(max_length=11)),
                ('medico_nome', models.CharField(max_length=255)),
                ('consulta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_rest.consulta')),
            ],
        ),
    ]