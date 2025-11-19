from django.db import models

# -------------------------
# PRODUCTOS
# -------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    grado_alcohol = models.CharField(max_length=20, blank=True, null=True)
    tipo_fruto = models.CharField(max_length=50, blank=True)
    pais_origen = models.CharField(max_length=50, blank=True)
    categoria = models.CharField(max_length=50, blank=True)     # Ahora campo de texto
    subcategoria = models.CharField(max_length=50, blank=True, default="Sin subcategoría")
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# -------------------------
# COMBOS
# -------------------------
class Combo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.IntegerField(default=1)

    categoria = models.CharField(max_length=50, blank=True)
    subcategoria = models.CharField(max_length=50, blank=True, default="Sin subcategoría")

    # 🔥 Campos necesarios para filtros
    festividad = models.CharField(max_length=50, blank=True)
    premium = models.CharField(max_length=50, blank=True)
    regalo = models.CharField(max_length=50, blank=True)

    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='combos/', null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


