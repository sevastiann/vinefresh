from django.db import models

# -------------------------
# CATEGORÍAS PRINCIPALES
# -------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# -------------------------
# SUBCATEGORÍAS (DINÁMICAS)
# -------------------------
class Subcategoria(models.Model):
    SECCIONES = [
        ('productos', 'Productos'),
        ('combos', 'Combos'),
    ]

    CATEGORIAS_PRINCIPALES = {
        'productos': [
            ('dulzor', 'Dulzor'),
            ('grado_alcohol', 'Grado de alcohol'),
            ('pais_origen', 'País de origen'),
            ('tipo_fruta', 'Tipo de fruta'),
            ('color', 'Color'),
        ],
        'combos': [
            ('festividad', 'Festividad'),
            ('temporada', 'Temporada'),
            ('ano_anejamiento', 'Año de añejamiento'),
        ],
    }

    categoria = models.ForeignKey(
        'Categoria',  # ✅ en string para evitar errores de orden
        on_delete=models.CASCADE,
        related_name="subcategorias",
        null=True,
        blank=True
    )

    seccion = models.CharField(max_length=50, choices=SECCIONES)
    categoria_principal = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)

    class Meta:
        unique_together = ('seccion', 'categoria_principal', 'nombre')
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"

    def __str__(self):
        return f"{self.get_seccion_display()} → {self.categoria_principal} → {self.nombre}"


# -------------------------
# PRODUCTOS
# -------------------------
class Producto(models.Model):
    nom_producto = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_unid = models.DecimalField(max_digits=10, decimal_places=2)
    grado_alcohol = models.DecimalField(max_digits=5, decimal_places=2)
    tipo_fruto = models.CharField(max_length=50)
    pais_origen = models.CharField(max_length=50)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    subcategoria = models.ForeignKey(
        Subcategoria,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.nom_producto


# -------------------------
# COMBOS
# -------------------------
class Combo(models.Model):
    nombre_combo = models.CharField(max_length=100)
    unidades = models.IntegerField()
    subcategoria = models.ForeignKey(
        Subcategoria,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.nombre_combo
