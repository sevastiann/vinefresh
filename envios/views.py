from django.shortcuts import render, get_object_or_404, redirect
from .models import Envio

# -----------------------------
# LISTAR ENVÍOS
# -----------------------------
def envios_listar(request):
    envios = Envio.objects.all()
    return render(request, 'envios/envios_listar.html', {'envios': envios})

# -----------------------------
# DETALLE DE ENVÍO
# -----------------------------
def envios_detalle(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    return render(request, 'envios/envios_detalle.html', {'envio': envio})

# -----------------------------
# CREAR ENVÍO
# -----------------------------
def envios_crear(request):
    return render(request, 'envios/envios_crear.html')

# -----------------------------
# EDITAR ENVÍO (CAMBIAR ESTADO)
# -----------------------------
def envios_editar(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)

    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        envio.estado = nuevo_estado
        envio.save()
        return redirect("envios_listar")

    return render(request, "envios/envios_editar.html", {"envio": envio})


# -----------------------------
# ELIMINAR ENVÍO
# -----------------------------
def envios_eliminar(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    return render(request, 'envios/envios_eliminar.html', {'envio': envio})

# -----------------------------
# SEGUIMIENTO DE UN ENVÍO
# -----------------------------
def seguimiento(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    return render(request, 'envios/seguimiento.html', {'envio': envio})

# -----------------------------
# RUTA DE UN ENVÍO
# -----------------------------
def rutas(request, envio_id):
    envio = get_object_or_404(Envio, id=envio_id)
    return render(request, 'envios/rutas.html', {'envio': envio})

# -----------------------------
# TRANSPORTADORES (GENERAL)
# -----------------------------
def transportadores(request):
    return render(request, 'envios/transportadores.html')
