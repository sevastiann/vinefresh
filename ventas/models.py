from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto, Combo


# ===========================
# 🛒 Carrito de Productos
# ===========================
class CarritoCompra(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='carrito'
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name='en_carrito'
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("usuario", "producto")

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.usuario.nombre} - {self.producto.nombre} ({self.cantidad})"


# ===========================
# 🛒 Carrito de Combos
# ===========================
class CarritoCombo(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="carrito_combos"
    )
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("usuario", "combo")

    def subtotal(self):
        return self.cantidad * self.combo.precio

    def __str__(self):
        return f"{self.usuario.nombre} - {self.combo.nombre} ({self.cantidad})"


# ===========================
# 📦 Pedido
# ===========================
class Pedido(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='pedidos'
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
        total_productos = sum(item.subtotal() for item in self.items.all())
        total_combos = sum(item.subtotal() for item in self.items_combos.all())
        return total_productos + total_combos

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.nombre}"

    class Meta:
        ordering = ['-fecha_pedido']


# ===========================
# 🧾 PedidoItem — SOLO productos
# ===========================
class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='items'
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()
    precio = models.FloatField()

    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


# ===========================
# 🧾 PedidoComboItem — SOLO combos
# ===========================
class PedidoComboItem(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='items_combos'
    )
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.FloatField()

    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.combo.nombre} x{self.cantidad}"


# ===========================
# 💳 Factura
# ===========================
class Factura(models.Model):
    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name='factura')
    fecha = models.DateField(auto_now_add=True)
    total_pagado = models.FloatField(default=0)

    def __str__(self):
        return f"Factura #{self.id} - {self.pedido.usuario.nombre}"


# ===========================
# 🎟️ Cupon
# ===========================
class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    fecha_expiracion = models.DateField()

    class Meta:
        ordering = ['-fecha_expiracion']

    def __str__(self):
        return f"{self.codigo} - {self.descuento}%"
