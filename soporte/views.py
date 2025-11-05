from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Soporte
from usuarios.models import Usuario

# Listar todas las solicitudes de soporte
def lista_soporte(request):
    soportes = list(Soporte.objects.values())
    return JsonResponse(soportes, safe=False)

# Ver una solicitud específica
def detalle_soporte(request, soporte_id):
    soporte = get_object_or_404(Soporte, id=soporte_id)
    data = {
        "id": soporte.id,
        "usuario": soporte.usuario.nombre_completo,
        "tipo": soporte.PQRS,
        "mensaje": soporte.mensaje,
        "estado": soporte.estado,
        "fecha": soporte.fecha,
    }
    return JsonResponse(data)

# Crear una nueva solicitud
def crear_soporte(request, usuario_id, tipo, mensaje):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    soporte = Soporte.objects.create(usuario=usuario, PQRS=tipo, mensaje=mensaje)
    return JsonResponse({"mensaje": f"Soporte creado por {usuario.nombre_completo} de tipo {tipo}"})

# Cambiar estado (por admin)
def cambiar_estado_soporte(request, soporte_id, nuevo_estado):
    soporte = get_object_or_404(Soporte, id=soporte_id)
    soporte.estado = nuevo_estado
    soporte.save()
    return JsonResponse({"mensaje": f"El soporte #{soporte.id} cambió a estado {nuevo_estado}"})
