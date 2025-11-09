from django.shortcuts import render, get_object_or_404, redirect
from .models import Soporte
from usuarios.models import Usuario

def lista_soporte(request):
    rol = request.session.get('usuario_rol', 'visitante')
    usuario_id = request.session.get('usuario_id')

    if rol == 'admin':
        soportes = Soporte.objects.all().order_by('-fecha')
    elif rol == 'cliente':
        soportes = Soporte.objects.filter(usuario_id=usuario_id).order_by('-fecha')
    else:
        soportes = []

    return render(request, 'soporte/listar_soporte.html', {'soportes': soportes, 'rol': rol})

def crear_soporte(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        usuario = get_object_or_404(Usuario, id=usuario_id)
        tipo = request.POST.get('tipo')
        mensaje = request.POST.get('mensaje')

        Soporte.objects.create(usuario=usuario, PQRS=tipo, mensaje=mensaje)
        return render(request, 'soporte/confirmacion.html', {'mensaje': 'Tu solicitud fue enviada con éxito.'})
    
    return render(request, 'soporte/nuevo_soporte.html')

def detalle_soporte(request, soporte_id):
    soporte = get_object_or_404(Soporte, id=soporte_id)
    return render(request, 'soporte/detalle_soporte.html', {'soporte': soporte})

def cambiar_estado_soporte(request, soporte_id, nuevo_estado):
    soporte = get_object_or_404(Soporte, id=soporte_id)
    soporte.estado = nuevo_estado
    soporte.save()
    return redirect('soporte:lista_soporte')
