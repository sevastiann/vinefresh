from django.db import models
from usuarios.models import Usuario

class Soporte(models.Model):
    PQRS_CHOICES = [
        ('Petición', 'Petición'),
        ('Queja', 'Queja'),
        ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'),
    ]
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En proceso', 'En proceso'),
        ('Resuelto', 'Resuelto'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    PQRS = models.CharField(max_length=20, choices=PQRS_CHOICES)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.PQRS} ({self.estado})"
