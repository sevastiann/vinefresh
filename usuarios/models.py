from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    nombre_usuario = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    password = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, default='cliente')
    solicitud_eliminacion = models.BooleanField(default=False)

# 🔹 Nuevo campo
    estado = models.BooleanField(default=True)  # True = activo, False = inactivo
    
    
    
    def __str__(self):
        return self.nombre_usuario


class InvitacionAdmin(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
