from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto

# --------------------------------------------------------
# CARRITO DE COMPRA
# --------------------------------------------------------
class CarritoCompra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrito')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='en_carritos')
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.producto.nom_producto} ({self.cantidad})"


# --------------------------------------------------------
# FACTURA
# --------------------------------------------------------
class Factura(models.Model):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='facturas')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Factura #{self.id} - {self.usuario.nombre_completo}"


# --------------------------------------------------------
# CUPÓN
# --------------------------------------------------------
class Cupon(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descuento = models.FloatField()
    fecha_expiracion = models.DateField()
    activo = models.BooleanField(default=True)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='cupones', null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} ({'Activo' if self.activo else 'Inactivo'})"


# --------------------------------------------------------
# PEDIDO
# --------------------------------------------------------
class Pedido(models.Model):
    carrito = models.ForeignKey(CarritoCompra, on_delete=models.CASCADE, related_name='pedidos')
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.FloatField()
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.carrito.usuario.nombre_completo}"
