from django.contrib import admin
from .models import Producto, Subcategoria, Combo

admin.site.register(Producto)
admin.site.register(Subcategoria)
admin.site.register(Combo)
