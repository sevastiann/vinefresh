from django.db import models
from django.utils import timezone

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    edad = models.IntegerField()
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    pais = models.CharField(max_length=50)
    nombre_usuario = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=200)
    fecha_registro = models.DateTimeField(default=timezone.now)

    # 🔑 Campo para roles
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='cliente')

    def __str__(self):
        return self.nombre_usuario
