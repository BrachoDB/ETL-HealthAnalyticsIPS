from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'ADMIN'
    MEDICO = 'MEDICO'
    ANALISTA = 'ANALISTA'

    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (MEDICO, 'Médico'),
        (ANALISTA, 'Analista'),
    ]

    ANALISTA_PERMISSIONS = [
        ('view_patient', 'Puede consultar pacientes del ETL'),
        ('view_etllog', 'Puede consultar logs del ETL'),
        ('view_kpi', 'Puede consultar indicadores analíticos'),
        ('export_analytics', 'Puede exportar datos analíticos'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEDICO)

    class Meta:
        permissions = ANALISTA_PERMISSIONS

    def __str__(self):
        return f'{self.username} - {self.get_role_display()}'
