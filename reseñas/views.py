from django.shortcuts import render, get_object_or_404, redirect
from .models import Reseña
from catalogo.models import Producto
from usuarios.models import Usuario

def lista_reseñas(request):
    reseñas = Reseña.objects.select_related('producto', 'usuario').order_by('-fecha')
    rol = request.session.get('usuario_rol', 'visitante')
    return render(request, 'reseñas/listar_reseñas.html', {'reseñas': reseñas, 'rol': rol})

def nueva_reseña(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return render(request, 'reseñas/confirmacion.html', {'mensaje': 'Debes iniciar sesión para dejar una reseña.'})

        usuario = get_object_or_404(Usuario, id=usuario_id)
        producto_id = request.POST.get('producto')
        calificacion = request.POST.get('calificacion')
        comentario = request.POST.get('comentario')

        producto = get_object_or_404(Producto, id=producto_id)

        Reseña.objects.create(
            usuario=usuario,
            producto=producto,
            calificacion=calificacion,
            comentario=comentario
        )

        return redirect('reseñas:lista_reseñas')  # redirige a la lista de reseñas

    productos = Producto.objects.all()
    return render(request, 'reseñas/nueva_reseña.html', {'productos': productos})

def detalle_reseña(request, reseña_id):
    reseña = get_object_or_404(Reseña, id=reseña_id)
    return render(request, 'reseñas/detalle_reseña.html', {'reseña': reseña})
