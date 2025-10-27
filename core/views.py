from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def home_view(request):
    usuario = None
    if 'usuario_id' in request.session:
        from usuarios.models import Usuario
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            usuario = None
    return render(request, 'core/home.html', {'usuario': usuario})
