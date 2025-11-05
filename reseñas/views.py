from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Reseña
from catalogo.models import Producto
from usuarios.models import Usuario

# Listar todas las reseñas
def lista_reseñas(request):
    reseñas = list(Reseña.objects.values())
    return JsonResponse(reseñas, safe=False)

# Detalle de una reseña específica
def detalle_reseña(request, reseña_id):
    reseña = get_object_or_404(Reseña, id=reseña_id)
    data = {
        "id": reseña.id,
        "producto": reseña.producto.nom_producto,
        "usuario": reseña.usuario.nombre_completo,
        "calificacion": reseña.calificacion,
        "comentario": reseña.comentario,
        "fecha": reseña.fecha,
    }
    return JsonResponse(data)

# Crear una nueva reseña (modo de prueba, sin formulario)
def crear_reseña(request, producto_id, usuario_id, calificacion, comentario=""):
    producto = get_object_or_404(Producto, id=producto_id)
    usuario = get_object_or_404(Usuario, id=usuario_id)
    reseña = Reseña.objects.create(
        producto=producto,
        usuario=usuario,
        calificacion=calificacion,
        comentario=comentario,
    )
    return JsonResponse({"mensaje": f"Reseña creada para {producto.nom_producto} por {usuario.nombre_completo}"})
