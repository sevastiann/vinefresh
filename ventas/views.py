from django.http import JsonResponse
from django.shortcuts import get_object_or_404,render,redirect
from .models import CarritoCompra, Pedido, Factura, Cupon
from catalogo.models import Producto
from usuarios.models import Usuario
from datetime import datetime
from django.contrib import messages

# --------------------------------------------------
# CARRITO
# --------------------------------------------------
def agregar_al_carrito(request, usuario_id, producto_id, cantidad):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    producto = get_object_or_404(Producto, id=producto_id)

    # Validar cantidad
    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return JsonResponse({"error": "La cantidad debe ser mayor que 0"}, status=400)
    except ValueError:
        return JsonResponse({"error": "La cantidad debe ser un número entero"}, status=400)

    carrito, creado = CarritoCompra.objects.get_or_create(
        usuario=usuario,
        producto=producto,
        defaults={"cantidad": 0}
    )

    carrito.cantidad += cantidad
    carrito.save()

    return JsonResponse({
        "mensaje": "Producto agregado al carrito",
        "producto": producto.nom_producto,
        "cantidad_agregada": cantidad,
        "cantidad_total": carrito.cantidad
    })


def ver_carrito(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = CarritoCompra.objects.filter(usuario=usuario).values(
        "id",
        "cantidad",
        "producto__nom_producto",
        "producto__precio"
    )
    return JsonResponse(list(carrito), safe=False)


# --------------------------------------------------
# FACTURA
# --------------------------------------------------
def crear_factura(request, usuario_id, metodo_pago):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    factura = Factura.objects.create(
        usuario=usuario,
        metodo_pago=metodo_pago
    )

    return JsonResponse({
        "mensaje": "Factura creada",
        "factura_id": factura.id,
        "usuario": f"{usuario.nombre} {usuario.apellido}",
        "metodo_pago": metodo_pago
    })

# -----------------------------
# CREAR FACTURA
# -----------------------------
def ventas_factura_crear(request):
    usuarios = Usuario.objects.all()

    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        metodo_pago = request.POST.get("metodo_pago")

        Factura.objects.create(
            usuario_id=usuario_id,
            metodo_pago=metodo_pago
        )

        messages.success(request, "✅ Factura creada correctamente")
        return redirect("ventas_facturas")

    return render(request, "ventas/ventas_factura_crear.html", {
        "usuarios": usuarios
    })

def ver_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return render(request, 'ventas/ventas_factura_ver.html', {'factura': factura})

def eliminar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    factura.delete()
    return redirect('ventas_facturas')

# --------------------------------------------------
# CUPONES
# --------------------------------------------------
def validar_cupon(request, codigo):
    cupon = get_object_or_404(Cupon, codigo=codigo)

    if not cupon.activo or cupon.fecha_expiracion < date.today():
        return JsonResponse({"mensaje": "Cupón inválido o expirado"}, status=400)

    return JsonResponse({
        "mensaje": "Cupón válido",
        "descuento": cupon.descuento
    })

# -----------------------------
# CREAR CUPÓN
# -----------------------------
def ventas_cupones_crear(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")
        descuento = request.POST.get("descuento")
        fecha_expiracion = request.POST.get("fecha_expiracion")
        activo = request.POST.get("activo") == "true"

        Cupon.objects.create(
            codigo=codigo,
            descuento=descuento,
            fecha_expiracion=fecha_expiracion,
            activo=activo
        )

        messages.success(request, "✅ Cupón creado exitosamente")
        return redirect("ventas_cupones")

    return render(request, "ventas/ventas_cupones_crear.html")

def eliminar_cupon(request, cupon_id):
    cupon = get_object_or_404(Cupon, id=cupon_id)
    cupon.delete()
    return redirect('ventas_cupones')

# --------------------------------------------------
# PEDIDOS
# --------------------------------------------------
def crear_pedido(request, carrito_id):
    """
    Crea un pedido usando el carrito.
    ✅ El precio se calcula automáticamente (seguro).
    """
    carrito = get_object_or_404(CarritoCompra, id=carrito_id)

    # Cálculo seguro del precio
    precio_final = carrito.producto.precio * carrito.cantidad

    pedido = Pedido.objects.create(
        carrito=carrito,
        cantidad=carrito.cantidad,
        precio=precio_final
    )

    return JsonResponse({
        "mensaje": "Pedido creado",
        "pedido_id": pedido.id,
        "producto": carrito.producto.nom_producto,
        "cantidad": carrito.cantidad,
        "precio_total": precio_final
    })


def ver_pedidos(request, usuario_id):
    pedidos = Pedido.objects.filter(carrito__usuario_id=usuario_id).values(
        "id",
        "cantidad",
        "precio",
        "carrito__producto__nom_producto",
        "carrito__producto__precio",
    )
    return JsonResponse(list(pedidos), safe=False)

# -----------------------------
# CREAR PEDIDO
# -----------------------------
def ventas_pedido_crear(request):
    carritos = CarritoCompra.objects.all()

    if request.method == "POST":
        carrito_id = request.POST.get("carrito_id")
        precio = request.POST.get("precio")

        Pedido.objects.create(
            carrito_id=carrito_id,
            precio_total=precio,
            fecha_pedido=datetime.now()
        )

        messages.success(request, "✅ Pedido creado correctamente")
        return redirect("ventas_pedidos")

    return render(request, "ventas/ventas_pedido_crear.html", {
        "carritos": carritos
    })

def ver_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'ventas/ventas_pedido_ver.html', {'pedido': pedido})

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    return redirect('ventas_pedidos')