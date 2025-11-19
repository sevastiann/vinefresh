from usuarios.models import Usuario

def get_current_usuario(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return Usuario.objects.filter(id=usuario_id).first()
