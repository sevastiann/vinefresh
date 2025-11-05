from django.shortcuts import render, redirect
from usuarios.models import Usuario

# Dashboard para clientes
def dashboard_cliente(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    return render(request, 'dashboard/cliente.html', {'usuario': usuario})


# Dashboard para administradores
def dashboard_admin(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    # Aquí puedes controlar que solo los admin entren
    if hasattr(usuario, 'rol') and usuario.rol == 'admin':
        return render(request, 'dashboard/admin.html', {'usuario': usuario})
    else:
        return redirect('dashboard_cliente')
