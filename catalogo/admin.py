from django.contrib import admin
from .models import Producto, Categoria, Combo

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Combo)
