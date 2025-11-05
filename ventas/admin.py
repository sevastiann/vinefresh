from django.contrib import admin
from .models import CarritoCompra, Pedido, Factura, Cupon

admin.site.register(CarritoCompra)
admin.site.register(Pedido)
admin.site.register(Factura)
admin.site.register(Cupon)
