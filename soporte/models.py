from django.db import models
from usuarios.models import Usuario

class Soporte(models.Model):
    ESTADOS = [
        ('Abierto', 'Abierto'),
        ('En proceso', 'En proceso'),
        ('Cerrado', 'Cerrado'),
    ]

    TIPO_PQRS = [
        ('Petición', 'Petición'),
        ('Queja', 'Queja'),
        ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='soportes')
    mensaje = models.TextField()
    PQRS = models.CharField(max_length=20, choices=TIPO_PQRS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Abierto')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.PQRS} de {self.usuario.nombre_completo} - {self.estado}"
