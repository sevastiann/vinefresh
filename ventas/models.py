from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto

class CarritoCompra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

class Pedido(models.Model):
    carrito = models.ForeignKey(CarritoCompra, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.FloatField()

class Factura(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)

class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    fecha_expiracion = models.DateField()
