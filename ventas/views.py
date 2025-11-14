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
# 📦 CREAR PEDIDO (FUNCIONAL Y LIMPIO)
# ============================================================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import CarritoCompra, Pedido, PedidoItem

def pedido_crear(request):
    usuario = request.user

    if not usuario.is_authenticated:
        messages.error(request, "Debes iniciar sesión para realizar un pedido.")
        return redirect("ventas:carrito")

    carrito = CarritoCompra.objects.filter(usuario=usuario)

    if not carrito.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect("ventas:carrito")

    # ============================
    # GET → Mostrar formulario
    # ============================
    if request.method == "GET":
        total_carrito = sum(item.producto.precio * item.cantidad for item in carrito)

        return render(request, "ventas/comprar.html", {
            "carrito_items": carrito,
            "total_carrito": total_carrito,
            "user": usuario
        })

    # ============================
    # POST → Crear pedido
    # ============================
    if request.method == "POST":
        metodo_pago = request.POST.get("metodo_pago")
        codigo_pago = request.POST.get("codigo_pago", "")

        if not metodo_pago:
            messages.error(request, "Debes seleccionar un método de pago.")
            return redirect("ventas:comprar.html")

        try:
            with transaction.atomic():

                pedido = Pedido.objects.create(usuario=usuario)

                for item in carrito:
                    PedidoItem.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio=item.producto.precio
                    )

                carrito.delete()

                return redirect("ventas:pago_exitoso")

        except Exception:
            messages.error(request, "Ocurrió un error al procesar el pedido.")
            return redirect("ventas:carrito")

    # ======================================
    # GET → Mostrar formulario de compra
    # ======================================
    total_carrito = sum(item.producto.precio * item.cantidad for item in carrito)

    return render(request, "ventas/comprar.html", {
        "carrito_items": carrito,
        "total_carrito": total_carrito,
        "user": usuario
    })


def pago_exitoso(request):
    return render(request, "ventas/pago_exitoso.html")


def pago_rechazado(request):
    return render(request, "ventas/pago_rechazado.html")



def pedidos_cliente(request):
    usuario = request.user
    if not hasattr(usuario, 'id') or usuario.id is None:
        # Si por alguna razón no es un usuario válido, retorna vacío
        pedidos = Pedido.objects.none()
    else:
        pedidos = Pedido.objects.filter(usuario=usuario).order_by("-id")

    return render(request, "ventas/pedidos.html", {"pedidos": pedidos})


def admin_pedidos(request):
    """Vista que carga el template de gestión de pedidos."""
    pedidos = Pedido.objects.all().order_by('-id')
    return render(request, "ventas/gestion_pedidos.html", {"pedidos": pedidos})

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Pedido

def actualizar_estado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        pedido.estado = nuevo_estado
        pedido.save()
        messages.success(request, f"✅ Estado del pedido #{pedido.id} actualizado a {nuevo_estado}.")
    return redirect("ventas:gestion_pedidos")


# ============================================================
# 🧾 FACTURAS
# ============================================================
import tempfile
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Pedido

def factura_pdf(request, pedido_id):
    # Obtener pedido del usuario actual
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Renderizar plantilla a HTML
    html_string = render_to_string('ventas/factura.html', {'pedido': pedido})
    
    # Crear PDF en memoria
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{pedido.id}.pdf"'
    
    # Generar PDF
    HTML(string=html_string).write_pdf(response)
    return response
