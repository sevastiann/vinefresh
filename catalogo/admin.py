from django.contrib import admin
from .models import Producto, Categoria, Inventario, Combo

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Inventario)
admin.site.register(Combo)
