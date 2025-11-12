from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto


# 🛒 Carrito individual del usuario
class CarritoCompra(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='en_carrito'
    )
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.usuario.nombre} - {self.producto.nombre} ({self.cantidad})"

    class Meta:
        verbose_name = "Carrito de compra"
        verbose_name_plural = "Carritos de compra"
        unique_together = ('usuario', 'producto')  # 🔒 evita duplicar el mismo producto en un carrito


# 📦 Pedido (conjunto de productos del carrito confirmados)
class Pedido(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=50,
        default='Pendiente',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Pagado', 'Pagado'),
            ('Enviado', 'Enviado'),
            ('Entregado', 'Entregado'),
            ('Cancelado', 'Cancelado'),
        ]
    )

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.nombre}"

    class Meta:
        ordering = ['-fecha_pedido']


# 🧾 Detalle de cada producto en el pedido
class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()
    precio = models.FloatField()

    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

    class Meta:
        verbose_name = "Item de pedido"
        verbose_name_plural = "Items de pedido"


# 💳 Factura ligada al pedido
class Factura(models.Model):
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='factura'
    )
    metodo_pago = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)
    total_pagado = models.FloatField(default=0)

    def __str__(self):
        return f"Factura #{self.id} - {self.pedido.usuario.nombre}"


# 🎟️ Cupones de descuento
class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.PositiveIntegerField(
        help_text="Porcentaje de descuento (0-100)"
    )
    activo = models.BooleanField(default=True)
    fecha_expiracion = models.DateField()

    def __str__(self):
        return f"{self.codigo} - {self.descuento}%"

    class Meta:
        ordering = ['-fecha_expiracion']
