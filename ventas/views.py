from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import date
from .models import CarritoCompra, Pedido, PedidoItem, Factura, Cupon
from catalogo.models import Producto
from usuarios.models import Usuario

# ============================================================
# 🛒 CARRITO
# ============================================================
def agregar_al_carrito(request, usuario_id, producto_id, cantidad):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    producto = get_object_or_404(Producto, id=producto_id)

    # Validar cantidad
    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return JsonResponse({"error": "La cantidad debe ser mayor que 0"}, status=400)
    except ValueError:
        return JsonResponse({"error": "La cantidad debe ser un número válido"}, status=400)

    # Crear o actualizar el carrito
    carrito, creado = CarritoCompra.objects.get_or_create(
        usuario=usuario,
        producto=producto,
        defaults={"cantidad": cantidad}
    )

    if not creado:
        carrito.cantidad += cantidad
        carrito.save()

    return JsonResponse({
        "mensaje": "Producto agregado al carrito",
        "producto": producto.nombre,
        "cantidad_total": carrito.cantidad
    })


def ver_carrito(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = CarritoCompra.objects.filter(usuario=usuario)

    data = [
        {
            "producto": item.producto.nombre,
            "precio_unitario": item.producto.precio,
            "cantidad": item.cantidad,
            "subtotal": item.subtotal(),
        }
        for item in carrito
    ]

    return JsonResponse(data, safe=False)


def carrito(request):
    """Versión HTML del carrito."""
    usuario = request.user
    carrito = CarritoCompra.objects.filter(usuario=usuario) if usuario.is_authenticated else []
    return render(request, "ventas/carrito.html", {"carrito": carrito})


# ============================================================
# 📦 PEDIDOS
# ============================================================
def pedido_crear(request):
    """Crea un pedido desde el carrito actual del usuario."""
    usuario = request.user
    carrito = CarritoCompra.objects.filter(usuario=usuario)

    if not carrito.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect("ventas:carrito_html")

    pedido = Pedido.objects.create(usuario=usuario)

    for item in carrito:
        PedidoItem.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio=item.producto.precio
        )

    carrito.delete()  # Vaciar el carrito tras crear el pedido
    messages.success(request, "✅ Pedido creado correctamente.")
    return redirect("ventas:pedidos_html")


def pedidos(request):
    """Muestra todos los pedidos del usuario."""
    usuario = request.user
    pedidos = Pedido.objects.filter(usuario=usuario)
    return render(request, "ventas/pedidos.html", {"pedidos": pedidos})


# ============================================================
# 🧾 FACTURAS
# ============================================================
def factura_crear(request):
    pedidos = Pedido.objects.all()

    if request.method == "POST":
        pedido_id = request.POST.get("pedido_id")
        metodo_pago = request.POST.get("metodo_pago")

        pedido = get_object_or_404(Pedido, id=pedido_id)
        total = pedido.total()

        Factura.objects.create(
            pedido=pedido,
            metodo_pago=metodo_pago,
            total_pagado=total
        )

        messages.success(request, "✅ Factura creada correctamente.")
        return redirect("ventas:facturas_html")

    return render(request, "ventas/factura_crear.html", {"pedidos": pedidos})


def facturas(request):
    """Lista de facturas creadas."""
    facturas = Factura.objects.all()
    return render(request, "ventas/facturas.html", {"facturas": facturas})


# ============================================================
# 🎟️ CUPONES
# ============================================================
def validar_cupon(request, codigo):
    cupon = get_object_or_404(Cupon, codigo=codigo)

    if not cupon.activo or cupon.fecha_expiracion < date.today():
        return JsonResponse({"mensaje": "Cupón inválido o expirado"}, status=400)

    return JsonResponse({
        "mensaje": "Cupón válido",
        "descuento": cupon.descuento
    })


def cupones_crear(request):
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

        messages.success(request, "✅ Cupón creado correctamente.")
        return redirect("ventas:cupones_html")

    return render(request, "ventas/cupones_crear.html")


def cupones(request):
    cupones = Cupon.objects.all()
    return render(request, "ventas/cupones.html", {"cupones": cupones})


# ============================================================
# 🌍 HOME
# ============================================================
def ventas_home(request):
    """Página principal de la app de ventas."""
    return render(request, "ventas/home.html")
