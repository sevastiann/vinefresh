from django.db import models
from catalogo.models import Producto  # relación con productos
from usuarios.models import Usuario   # relación con quien hace la reseña

class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='reseñas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reseñas')
    calificacion = models.IntegerField(default=1)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario.nombre_completo} - {self.producto.nom_producto} ({self.calificacion}/5)"
