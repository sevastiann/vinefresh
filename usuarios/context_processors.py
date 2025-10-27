from .models import Usuario

def usuario_logueado(request):
    usuario = None
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            usuario = None
    print("Context processor: usuario =", usuario)  # <- para depurar
    return {'usuario': usuario}
