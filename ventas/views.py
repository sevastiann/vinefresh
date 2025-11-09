from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import CarritoCompra, Pedido, Factura, Cupon
from catalogo.models import Producto
from usuarios.models import Usuario
from datetime import date


# -----------------------------
# CARRITO
# -----------------------------
def agregar_al_carrito(request, usuario_id, producto_id, cantidad):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    producto = get_object_or_404(Producto, id=producto_id)

    carrito, creado = CarritoCompra.objects.get_or_create(usuario=usuario, producto=producto)
    carrito.cantidad += int(cantidad)
    carrito.save()

    return JsonResponse({
        "mensaje": f"{cantidad} unidad(es) de {producto.nom_producto} agregadas al carrito."
    })


def ver_carrito(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = list(CarritoCompra.objects.filter(usuario=usuario).values())
    return JsonResponse(carrito, safe=False)


# -----------------------------
# FACTURA
# -----------------------------
def crear_factura(request, usuario_id, metodo_pago):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    factura = Factura.objects.create(usuario=usuario, metodo_pago=metodo_pago)
    return JsonResponse({
        "mensaje": f"Factura #{factura.id} creada para {usuario.nombre} {usuario.apellido}"
    })


# -----------------------------
# CUPÓN
# -----------------------------
def validar_cupon(request, codigo):
    cupon = get_object_or_404(Cupon, codigo=codigo)
    
    if not cupon.activo or cupon.fecha_expiracion < date.today():
        return JsonResponse({"mensaje": "Cupón inválido o expirado"})
    
    return JsonResponse({
        "mensaje": f"Cupón válido. Descuento: {cupon.descuento}%"
    })


# -----------------------------
# PEDIDOS
# -----------------------------
def crear_pedido(request, carrito_id, precio):
    """Crea un pedido a partir de un carrito."""
    carrito = get_object_or_404(CarritoCompra, id=carrito_id)
    precio = float(precio)

    pedido = Pedido.objects.create(
        carrito=carrito,
        cantidad=carrito.cantidad,
        precio=precio
    )

    return JsonResponse({
        "mensaje": f"Pedido #{pedido.id} creado para {carrito.usuario.nombre} {carrito.usuario.apellido}"
    })


def ver_pedidos(request, usuario_id):
    pedidos = list(Pedido.objects.filter(carrito__usuario_id=usuario_id).values())
    return JsonResponse(pedidos, safe=False)



# -----------------------------
# FAVORITOS
# -----------------------------
def favoritos(request):
    """Renderiza la página de favoritos (aunque esté vacía)."""
    return render(request, 'core/home.html')


def agregar_favorito(request, usuario_id, producto_id):
    """Ejemplo de función para agregar a favoritos (sin romper si no hay modelo todavía)."""
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        producto = get_object_or_404(Producto, id=producto_id)
        # Si más adelante creas un modelo Favorito, aquí se guardaría.
        return JsonResponse({"mensaje": f"{producto.nom_producto} agregado a favoritos de {usuario.nombre}"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
