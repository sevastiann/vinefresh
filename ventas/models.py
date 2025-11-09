from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import CarritoCompra, Pedido, Factura, Cupon
from catalogo.models import Producto
from usuarios.models import Usuario
from datetime import date


# -------------------------------------------------------------------
#                           CARRITO
# -------------------------------------------------------------------

def agregar_al_carrito(request, usuario_id, producto_id, cantidad):
    """Agrega productos al carrito (sumando si ya existe)."""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    producto = get_object_or_404(Producto, id=producto_id)

    carrito, creado = CarritoCompra.objects.get_or_create(
        usuario=usuario,
        producto=producto
    )

    carrito.cantidad += int(cantidad)
    carrito.save()

    return JsonResponse({
        "mensaje": f"{cantidad} unidad(es) agregadas al carrito.",
        "carrito_id": carrito.id
    })


def ver_carrito(request, usuario_id):
    """Devuelve todos los productos del carrito del usuario."""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = list(CarritoCompra.objects.filter(usuario=usuario).values())

    return JsonResponse(carrito, safe=False)


# -------------------------------------------------------------------
#                           PEDIDOS
# -------------------------------------------------------------------

def crear_pedido(request, carrito_id, precio):
    """Crea un pedido basado en un carrito existente."""
    carrito = get_object_or_404(CarritoCompra, id=carrito_id)

    pedido = Pedido.objects.create(
        carrito=carrito,
        cantidad=carrito.cantidad,
        precio=float(precio)
    )

    return JsonResponse({
        "mensaje": f"Pedido #{pedido.id} creado correctamente",
        "pedido_id": pedido.id
    })


def ver_pedidos(request, usuario_id):
    """Lista todos los pedidos pertenecientes a un usuario."""
    pedidos = list(
        Pedido.objects.filter(
            carrito__usuario_id=usuario_id
        ).values()
    )

    return JsonResponse(pedidos, safe=False)


# -------------------------------------------------------------------
#                           FACTURAS
# -------------------------------------------------------------------

def crear_factura(request, usuario_id, metodo_pago):
    """Crea una factura para un usuario."""
    usuario = get_object_or_404(Usuario, id=usuario_id)

    factura = Factura.objects.create(
        usuario=usuario,
        metodo_pago=metodo_pago
    )

    return JsonResponse({
        "mensaje": f"Factura #{factura.id} creada",
        "factura_id": factura.id
    })


# -------------------------------------------------------------------
#                           CUPONES
# -------------------------------------------------------------------

def validar_cupon(request, codigo):
    """Valida si un cupón existe, está activo y no está expirado."""
    cupon = get_object_or_404(Cupon, codigo=codigo)

    if not cupon.activo:
        return JsonResponse({"mensaje": "El cupón está desactivado"})

    if cupon.fecha_expiracion < date.today():
        return JsonResponse({"mensaje": "El cupón está expirado"})

    return JsonResponse({
        "mensaje": f"Cupón válido ({cupon.descuento}%)",
        "descuento": cupon.descuento
    })


# -------------------------------------------------------------------
#                           HTML PAGES
# -------------------------------------------------------------------

def ventas_home(request):
    return render(request, "ventas/home.html")

def ventas_carrito(request):
    return render(request, "ventas/carrito.html")

def ventas_pedidos(request):
    return render(request, "ventas/pedidos.html")

def ventas_facturas(request):
    return render(request, "ventas/facturas.html")

def ventas_cupones(request):
    return render(request, "ventas/cupones.html")
