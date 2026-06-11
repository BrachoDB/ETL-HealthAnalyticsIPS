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
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEDICO)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
