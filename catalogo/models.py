from django.db import models

class Categoria(models.Model):
    color = models.CharField(max_length=50)
    azucar = models.CharField(max_length=50)
    gas_carbonico = models.CharField(max_length=50)
    crianza_barrica = models.CharField(max_length=50)

    def __str__(self):
        return f"Categoría {self.id} - {self.color}"


class Producto(models.Model):
    nom_producto = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_unid = models.DecimalField(max_digits=10, decimal_places=2)
    grado_alcohol = models.DecimalField(max_digits=5, decimal_places=2)
    tipo_fruto = models.CharField(max_length=50)
    pais_origen = models.CharField(max_length=50)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom_producto


class Combo(models.Model):
    nombre_combo = models.CharField(max_length=100)
    unidades = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_combo
