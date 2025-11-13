from django.shortcuts import render, get_object_or_404, redirect
from .models import Soporte
from usuarios.models import Usuario
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# Listado general de soporte
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

# Crear nuevo soporte (PQRS)
def crear_soporte(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        usuario = get_object_or_404(Usuario, id=usuario_id)
        tipo = request.POST.get('tipo')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')

        Soporte.objects.create(usuario=usuario, PQRS=tipo, asunto=asunto, mensaje=mensaje)
        return render(request, 'soporte/confirmacion.html', {'mensaje': 'Tu solicitud fue enviada con éxito.'})
    
    return render(request, 'soporte/nuevo_soporte.html')

# Ver detalle de una solicitud (cliente/admin)
def detalle_soporte(request, soporte_id):
    soporte = get_object_or_404(Soporte, id=soporte_id)
    rol = request.session.get('usuario_rol', 'visitante')

    return render(request, 'soporte/detalle_soporte.html', {'soporte': soporte, 'rol': rol})

# Panel del administrador para ver PQRS separados
def panel_admin_soporte(request):
    if request.session.get('usuario_rol') != 'admin':
        return redirect('core:home')
    
    pqrs = {
        'Peticiones': Soporte.objects.filter(PQRS='Petición').order_by('-fecha'),
        'Quejas': Soporte.objects.filter(PQRS='Queja').order_by('-fecha'),
        'Reclamos': Soporte.objects.filter(PQRS='Reclamo').order_by('-fecha'),
        'Sugerencias': Soporte.objects.filter(PQRS='Sugerencia').order_by('-fecha'),
    }

    return render(request, 'soporte/panel_admin.html', {'pqrs': pqrs})

# Responder y actualizar PQRS (admin)
def responder_soporte(request, soporte_id):
    if request.session.get('usuario_rol') != 'admin':
        return redirect('core:home')

    soporte = get_object_or_404(Soporte, id=soporte_id)

    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        nuevo_estado = request.POST.get('estado')

        if respuesta:
            soporte.respuesta = respuesta
            soporte.fecha_respuesta = timezone.now()
            if nuevo_estado:
                soporte.estado = nuevo_estado
            soporte.save()

            # Enviar correo al cliente
            asunto_email = f"Respuesta a tu solicitud de soporte: {soporte.PQRS}"
            mensaje_email = f"""
Hola {soporte.usuario.nombre},

Tu solicitud de soporte ha sido respondida:

Asunto: {soporte.PQRS} {f' - {soporte.asunto}' if soporte.asunto else ''}
Mensaje enviado: {soporte.mensaje}

Respuesta del administrador:
{soporte.respuesta}

Estado actual de tu solicitud: {soporte.estado}

Puedes ver el estado de tu solicitud ingresando a tu panel.

Saludos,
Equipo de Soporte
            """

            try:
                send_mail(
                    asunto_email,
                    mensaje_email,
                    settings.DEFAULT_FROM_EMAIL,
                    [soporte.usuario.email],
                    fail_silently=False,
                )
                print(f"Correo enviado correctamente a {soporte.usuario.email}")
            except Exception as e:
                print("Error al enviar correo:", e)

            return redirect('soporte:panel_admin_soporte')

    return render(request, 'soporte/responder_soporte.html', {'soporte': soporte})
