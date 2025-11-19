# ventas/views.py (VERSIÓN CORREGIDA)
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction

# Modelos de esta app y relacionados
from .models import CarritoCompra, Pedido, PedidoItem, Factura, Cupon
from catalogo.models import Producto
from usuarios.models import Usuario

# Librería para PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


# ---------------------------
# Helper: obtener usuario actual (por sesión)
# ---------------------------
def get_current_usuario(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return Usuario.objects.filter(id=usuario_id).first()


# ============================================================
# 🛒 VER CARRITO EN HTML
# ============================================================
def carrito(request):
    carrito_items = []
    total = 0

    usuario = get_current_usuario(request)

    if usuario:
        # Carrito desde DB para usuarios logueados
        carrito = CarritoCompra.objects.filter(usuario=usuario)
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
    usuario = get_current_usuario(request)

    if usuario:
        # Usuario logueado → carrito en DB (evita duplicados por unique_together)
        carrito_obj, creado = CarritoCompra.objects.get_or_create(
            usuario=usuario,
            producto=producto,
            defaults={"cantidad": 1}
        )
        if not creado:
            carrito_obj.cantidad += 1
            carrito_obj.save()
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

    usuario = get_current_usuario(request)
    if usuario:
        carrito_item = get_object_or_404(CarritoCompra, id=item_id, usuario=usuario)
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

    usuario = get_current_usuario(request)
    if usuario:
        carrito_item = get_object_or_404(CarritoCompra, id=item_id, usuario=usuario)
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
def pedido_crear(request):
    usuario = get_current_usuario(request)

    if not usuario:
        messages.error(request, "Debes iniciar sesión para realizar un pedido.")
        return redirect("ventas:carrito")

    carrito = CarritoCompra.objects.filter(usuario=usuario)

    if not carrito.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect("ventas:carrito")

    # GET → Mostrar formulario de compra
    if request.method == "GET":
        total_carrito = sum(item.producto.precio * item.cantidad for item in carrito)
        return render(request, "ventas/comprar.html", {
            "carrito_items": carrito,
            "total_carrito": total_carrito,
            "user": usuario
        })

    # POST → Procesar pedido
    if request.method == "POST":
        metodo_pago = request.POST.get("metodo_pago")
        codigo_pago = request.POST.get("codigo_pago", "")

        if not metodo_pago:
            messages.error(request, "Debes seleccionar un método de pago.")
            return redirect("ventas:pedido_crear")  # nombre de la vista

        try:
            with transaction.atomic():
                # Crear pedido
                pedido = Pedido.objects.create(usuario=usuario)

                # Crear items del pedido
                for item in carrito:
                    PedidoItem.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio=item.producto.precio
                    )

                # Marcar pedido como pagado si hubo método de pago (simple lógica)
                # Aquí podrías integrar con pasarela real y verificar el pago
                pedido.estado = "Pagado"
                pedido.save()

                # Crear factura asociada
                factura_total = pedido.total()
                Factura.objects.create(
                    pedido=pedido,
                    metodo_pago=metodo_pago,
                    fecha=date.today(),
                    total_pagado=factura_total
                )

                # Vaciar carrito del usuario
                carrito.delete()

                messages.success(request, "✅ Pedido realizado correctamente.")
                return redirect("ventas:pago_exitoso")

        except Exception as e:
            # Registramos el error (en producción sería logger)
            messages.error(request, "Ocurrió un error al procesar el pedido.")
            return redirect("ventas:carrito")


# Páginas de resultado
def pago_exitoso(request):
    return render(request, "ventas/pago_exitoso.html")


def pago_rechazado(request):
    return render(request, "ventas/pago_rechazado.html")


# ============================================================
# 🧾 LISTADO DE PEDIDOS - Cliente
# ============================================================
def pedidos_cliente(request):
    usuario = get_current_usuario(request)
    if not usuario:
        messages.error(request, "Debes iniciar sesión para ver tus pedidos.")
        return redirect("usuarios:login")  # o donde tengas la vista de login

    pedidos = Pedido.objects.filter(usuario=usuario).order_by("-id")
    return render(request, "ventas/pedidos.html", {"pedidos": pedidos})


# ============================================================
# 🧾 GESTIÓN DE PEDIDOS - Admin
# ============================================================
from usuarios.utils import get_current_usuario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ventas.models import Pedido


# 📌 Página donde el admin ve TODOS los pedidos
def admin_pedidos(request):
    usuario = get_current_usuario(request)

    # Validar que sea admin
    if not usuario or usuario.rol != "admin":
        messages.error(request, "Acceso denegado.")
        return redirect("core:home")

    pedidos = Pedido.objects.all().order_by("-id")

    return render(request, "ventas/gestion_pedidos.html", {
        "pedidos": pedidos
    })


# 📌 Actualizar estado del pedido
def actualizar_estado(request, pedido_id):
    usuario = get_current_usuario(request)

    # Validar rol admin
    if not usuario or usuario.rol != "admin":
        messages.error(request, "Acceso denegado.")
        return redirect("core:home")

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")

        if nuevo_estado:
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f"El estado del pedido #{pedido.id} ha sido actualizado a {nuevo_estado}.")

    return redirect("ventas:gestion_pedidos")



# ============================================================
# 🧾 FACTURA (PDF)
# ============================================================
def factura_pdf(request, pedido_id):
    usuario = get_current_usuario(request)
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Validar que el usuario puede ver esa factura (propietario o admin)
    if not usuario:
        messages.error(request, "Debes iniciar sesión para ver la factura.")
        return redirect("usuarios:login")

    if pedido.usuario != usuario and usuario.rol != "admin":
        messages.error(request, "No tienes permiso para ver esta factura.")
        return redirect("core:home")

    # Preparar el response como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{pedido.id}.pdf"'

    # Crear PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, f"Factura #{pedido.id}")

    # Datos del usuario
    p.setFont("Helvetica", 12)
    nombre_usuario = pedido.usuario.nombre_usuario if hasattr(pedido.usuario, "nombre_usuario") else str(pedido.usuario)
    p.drawString(1 * inch, height - 1.4 * inch, f"Cliente: {nombre_usuario}")
    p.drawString(1 * inch, height - 1.7 * inch, f"Fecha: {pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M')}")

    # Línea separadora
    p.line(1 * inch, height - 1.9 * inch, width - 1 * inch, height - 1.9 * inch)

    # Encabezado
    y = height - 2.2 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, y, "Producto")
    p.drawString(3.5 * inch, y, "Cantidad")
    p.drawString(5 * inch, y, "Precio")
    p.drawString(6.2 * inch, y, "Subtotal")

    y -= 0.3 * inch
    p.setFont("Helvetica", 12)

    # Items del pedido
    for item in pedido.items.all():
        # nombre, cantidad, precio individual y subtotal
        p.drawString(1 * inch, y, str(item.producto.nombre)[:30])
        p.drawString(3.5 * inch, y, str(item.cantidad))
        p.drawString(5 * inch, y, f"${item.precio:.2f}")
        p.drawString(6.2 * inch, y, f"${item.subtotal():.2f}")

        y -= 0.25 * inch

        # Evitar que el texto salga de la página
        if y < 1 * inch:
            p.showPage()
            y = height - 1 * inch

    # Total final
    y -= 0.2 * inch
    p.setFont("Helvetica-Bold", 13)
    p.drawString(1 * inch, y, f"Total a pagar: ${pedido.total():.2f}")

    # Finalizar
    p.showPage()
    p.save()

    return response