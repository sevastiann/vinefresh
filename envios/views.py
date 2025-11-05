from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Envio

def lista_envios(request):
    envios = list(Envio.objects.values())
    return JsonResponse(envios, safe=False)

def detalle_envio(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    data = {
        "id": envio.id,
        "estado": envio.estado,
        "fecha_envio": envio.fecha_envio,
    }
    return JsonResponse(data)

def cambiar_estado_envio(request, envio_id, nuevo_estado):
    envio = get_object_or_404(Envio, id=envio_id)
    envio.estado = nuevo_estado
    envio.save()
    return JsonResponse({"mensaje": f"Estado del envío {envio_id} cambiado a {nuevo_estado}"})
