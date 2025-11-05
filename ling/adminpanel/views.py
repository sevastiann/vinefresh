from django.shortcuts import render
from usuarios.models import Usuario
from inventario.models import Producto

def dashboard(request):
    total_usuarios = Usuario.objects.count()
    total_productos = Producto.objects.count()
    return render(request, 'adminpanel/dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
    })

def perfil_admin(request):
    # Podrías obtener el admin logueado desde sesión o request.user
    admin = Usuario.objects.filter(rol='admin').first()
    if request.method == 'POST':
        admin.nombre = request.POST.get('nombre')
        admin.correo = request.POST.get('correo')
        admin.save()
    return render(request, 'admin_panel/perfil.html', {'admin': admin})

def configuracion(request):
    return render(request, 'admin_panel/configuracion.html')

def estadisticas(request):
    return render(request, 'admin_panel/estadisticas.html')
