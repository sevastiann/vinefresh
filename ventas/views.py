from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import date
from .models import CarritoCompra, Pedido, PedidoItem, Factura, Cupon
from catalogo.models import Producto
from usuarios.models import Usuario


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto, CarritoCompra

# ============================================================
# 🛒 VER CARRITO EN HTML
# ============================================================

def carrito(request):
    carrito_items = []
    total = 0

    if request.user.is_authenticated:
        # Carrito desde DB para usuarios logueados
        carrito = CarritoCompra.objects.filter(usuario=request.user)
        for item in carrito:
            subtotal = item.producto.precio * item.cantidad
            carrito_items.append({
                "id": item.id,
                "producto": item.producto,
                "cantidad": item.cantidad,
                "subtotal": subtotal
            })
            total += subtotal
    else:
        # Carrito desde sesión para usuarios no logueados
        carrito_sesion = request.session.get("carrito", {})
        for pid, cantidad in carrito_sesion.items():
            producto = get_object_or_404(Producto, id=pid)
            subtotal = producto.precio * cantidad
            carrito_items.append({
                "id": pid,
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal
            })
            total += subtotal

    context = {
        "carrito": carrito_items,
        "total": total,
    }

    return render(request, "ventas/carrito.html", context)



# ============================================================
# 🛒 AGREGAR PRODUCTO AL CARRITO
# ============================================================
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.user.is_authenticated:
        # Usuario logueado → carrito en DB
        carrito, creado = CarritoCompra.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={"cantidad": 1}
        )
        if not creado:
            carrito.cantidad += 1
            carrito.save()
    else:
        # Usuario anónimo → carrito en sesión
        carrito_sesion = request.session.get("carrito", {})
        pid = str(producto.id)
        carrito_sesion[pid] = carrito_sesion.get(pid, 0) + 1
        request.session["carrito"] = carrito_sesion

    return redirect("ventas:carrito")


# ============================================================
# 🛒 ACTUALIZAR CANTIDAD
# ============================================================
def actualizar_cantidad(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    nueva_cantidad = request.POST.get("cantidad", None)
    if nueva_cantidad is None:
        return JsonResponse({"error": "No se recibió cantidad"}, status=400)

    try:
        nueva_cantidad = int(nueva_cantidad)
        if nueva_cantidad <= 0:
            return JsonResponse({"error": "La cantidad debe ser mayor que 0"}, status=400)
    except ValueError:
        return JsonResponse({"error": "La cantidad debe ser un número válido"}, status=400)

    if request.user.is_authenticated:
        carrito_item = get_object_or_404(CarritoCompra, id=item_id, usuario=request.user)
        carrito_item.cantidad = nueva_cantidad
        carrito_item.save()
    else:
        # Usuario anónimo → actualizar cantidad en sesión
        carrito_sesion = request.session.get("carrito", {})
        pid = str(item_id)
        if pid in carrito_sesion:
            carrito_sesion[pid] = nueva_cantidad
            request.session["carrito"] = carrito_sesion
        else:
            return JsonResponse({"error": "Producto no encontrado en el carrito"}, status=404)

    return JsonResponse({"mensaje": "Cantidad actualizada", "item_id": item_id, "cantidad_total": nueva_cantidad})


# ============================================================
# 🛒 ELIMINAR PRODUCTO DEL CARRITO
# ============================================================
def eliminar_del_carrito(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    if request.user.is_authenticated:
        carrito_item = get_object_or_404(CarritoCompra, id=item_id, usuario=request.user)
        carrito_item.delete()
    else:
        carrito_sesion = request.session.get("carrito", {})
        pid = str(item_id)
        if pid in carrito_sesion:
            carrito_sesion.pop(pid)
            request.session["carrito"] = carrito_sesion
        else:
            return JsonResponse({"error": "Producto no encontrado en el carrito"}, status=404)

    return JsonResponse({"mensaje": "Producto eliminado del carrito", "item_id": item_id})

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
