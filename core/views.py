# core/views.py
from django.shortcuts import render
from usuarios.models import Usuario

def home(request):
    usuario = None
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            usuario = None
    return render(request, 'core/home.html', {'usuario': usuario})


def contacto(request):
    return render(request, 'core/contacto.html')

def nosotros(request):
    return render(request, 'core/nosotros.html')

def privacidad(request):
    return render(request, 'core/privacidad.html')

def terminos(request):
    return render(request, 'core/terminos.html')
