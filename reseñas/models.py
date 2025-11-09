from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto  # ajusta si tu modelo de productos está en otra app

class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calificacion = models.IntegerField(choices=[(i, f"{i} estrellas") for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.producto.nom_producto} ({self.calificacion}⭐)"
