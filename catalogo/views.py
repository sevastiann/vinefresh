from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Producto, Categoria, Combo

def lista_productos(request):
    productos = list(Producto.objects.values())
    return JsonResponse(productos, safe=False)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    data = {
        "id": producto.id,
        "nombre": producto.nom_producto,
        "descripcion": producto.descripcion,
        "precio_unid": float(producto.precio_unid),
        "grado_alcohol": float(producto.grado_alcohol),
        "tipo_fruto": producto.tipo_fruto,
        "pais_origen": producto.pais_origen,
        "categoria": producto.categoria.color,
    }
    return JsonResponse(data)

def lista_categorias(request):
    categorias = list(Categoria.objects.values())
    return JsonResponse(categorias, safe=False)

def lista_combos(request):
    combos = list(Combo.objects.values())
    return JsonResponse(combos, safe=False)
