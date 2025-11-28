# ventas/views.py
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction

# Modelos
from .models import (
    CarritoCompra,
    CarritoCombo,
    Pedido,
    PedidoItem,
    PedidoComboItem,
    Factura,
    Cupon
)
from catalogo.models import Producto, Combo
from usuarios.models import Usuario

# PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


# ============================================================
# 🔑 Helper: Usuario actual desde la sesión
# ============================================================
def get_current_usuario(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return Usuario.objects.filter(id=usuario_id).first()



# ============================================================
# 🛒 VER CARRITO
# ============================================================
def carrito(request):
    carrito_items = []
    total = 0

    usuario = get_current_usuario(request)

    if usuario:
        # ---------- Productos ----------
        carrito_productos = CarritoCompra.objects.filter(usuario=usuario)
        for item in carrito_productos:
            subtotal = item.producto.precio * item.cantidad
            carrito_items.append({
                "id": f"prod-{item.id}",
                "producto": item.producto,
                "cantidad": item.cantidad,
                "subtotal": subtotal,
                "es_combo": False
            })
            total += subtotal

        # ---------- Combos ----------
        carrito_combos = CarritoCombo.objects.filter(usuario=usuario)
        for item in carrito_combos:
            subtotal = item.combo.precio * item.cantidad
            carrito_items.append({
                "id": f"combo-{item.id}",
                "producto": item.combo,
                "cantidad": item.cantidad,
                "subtotal": subtotal,
                "es_combo": True
            })
            total += subtotal

    else:
        # ---------- Productos en sesión ----------
        carrito_sesion = request.session.get("carrito", {})
        for pid, cantidad in carrito_sesion.items():
            producto = get_object_or_404(Producto, id=pid)
            subtotal = producto.precio * cantidad
            carrito_items.append({
                "id": f"prod-{pid}",
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
                "es_combo": False
            })
            total += subtotal

        # ---------- Combos en sesión ----------
        carrito_sesion_combos = request.session.get("carrito_combos", {})
        for cid, cantidad in carrito_sesion_combos.items():
            combo = get_object_or_404(Combo, id=cid)
            subtotal = combo.precio * cantidad
            carrito_items.append({
                "id": f"combo-{cid}",
                "producto": combo,
                "cantidad": cantidad,
                "subtotal": subtotal,
                "es_combo": True
            })
            total += subtotal

    return render(request, "ventas/carrito.html", {
        "carrito": carrito_items,
        "total": total
    })



# ============================================================
# 🛒 AGREGAR PRODUCTO
# ============================================================
def agregar_al_carrito(request, producto_id):
    usuario = get_current_usuario(request)
    producto = get_object_or_404(Producto, id=producto_id)

    if usuario:
        obj, creado = CarritoCompra.objects.get_or_create(
            usuario=usuario,
            producto=producto,
            defaults={"cantidad": 1}
        )
        if not creado:
            obj.cantidad += 1
            obj.save()
    else:
        carrito = request.session.get("carrito", {})
        pid = str(producto.id)
        carrito[pid] = carrito.get(pid, 0) + 1
        request.session["carrito"] = carrito

    return redirect("ventas:carrito")

# ============================================================
# 🛒 AGREGAR COMBO AL CARRITO
# ============================================================
def agregar_combo_al_carrito(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id)
    usuario = get_current_usuario(request)

    if usuario:
        item, creado = CarritoCombo.objects.get_or_create(
            usuario=usuario,
            combo=combo,
            defaults={"cantidad": 1}
        )
        if not creado:
            item.cantidad += 1
            item.save()
    else:
        carrito_sesion = request.session.get("carrito_combos", {})
        cid = str(combo_id)
        carrito_sesion[cid] = carrito_sesion.get(cid, 0) + 1
        request.session["carrito_combos"] = carrito_sesion

    return redirect("ventas:carrito")


# ============================================================
# 🛒 ACTUALIZAR CANTIDAD PRODUCTO
# ============================================================
def actualizar_cantidad(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    cantidad = request.POST.get("cantidad")

    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return JsonResponse({"error": "Cantidad inválida"}, status=400)
    except:
        return JsonResponse({"error": "Cantidad inválida"}, status=400)

    usuario = get_current_usuario(request)

    if usuario:
        item = get_object_or_404(CarritoCompra, id=item_id, usuario=usuario)
        item.cantidad = cantidad
        item.save()
    else:
        carrito = request.session.get("carrito", {})
        pid = str(item_id)
        if pid in carrito:
            carrito[pid] = cantidad
            request.session["carrito"] = carrito
        else:
            return JsonResponse({"error": "No encontrado"}, status=404)

    return JsonResponse({"mensaje": "OK"})



# ============================================================
# 🛒 ELIMINAR PRODUCTO DEL CARRITO
# ============================================================
def eliminar_del_carrito(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    usuario = get_current_usuario(request)

    # Determinar tipo
    if str(item_id).startswith("prod-"):
        real_id = item_id.replace("prod-", "")

        if usuario:
            item = get_object_or_404(CarritoCompra, id=real_id, usuario=usuario)
            item.delete()
        else:
            carrito = request.session.get("carrito", {})
            if real_id in carrito:
                carrito.pop(real_id)
                request.session["carrito"] = carrito

    elif str(item_id).startswith("combo-"):
        real_id = item_id.replace("combo-", "")

        if usuario:
            item = get_object_or_404(CarritoCombo, id=real_id, usuario=usuario)
            item.delete()
        else:
            carrito = request.session.get("carrito_combos", {})
            if real_id in carrito:
                carrito.pop(real_id)
                request.session["carrito_combos"] = carrito

    else:
        return JsonResponse({"error": "ID inválido"}, status=400)

    return JsonResponse({"mensaje": "OK"})

# ============================================================
# 📦 CREAR PEDIDO (PRODUCTOS + COMBOS)
# ============================================================
def pedido_crear(request):
    usuario = get_current_usuario(request)

    if not usuario:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("ventas:carrito")

    carrito_prod = CarritoCompra.objects.filter(usuario=usuario)
    carrito_combo = CarritoCombo.objects.filter(usuario=usuario)

    if not carrito_prod.exists() and not carrito_combo.exists():
        messages.error(request, "El carrito está vacío.")
        return redirect("ventas:carrito")

    # GET → mostrar resumen
    if request.method == "GET":
        total = sum(i.producto.precio * i.cantidad for i in carrito_prod)
        total += sum(i.combo.precio * i.cantidad for i in carrito_combo)

        return render(request, "ventas/comprar.html", {
            "carrito_items": carrito_prod,
            "carrito_combos": carrito_combo,
            "total_carrito": total
        })

    # POST → crear pedido
    try:
        with transaction.atomic():
            pedido = Pedido.objects.create(usuario=usuario)

            # Productos
            for item in carrito_prod:
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio=item.producto.precio
                )

            # Combos
            for item in carrito_combo:
                PedidoComboItem.objects.create(
                    pedido=pedido,
                    combo=item.combo,
                    cantidad=item.cantidad,
                    precio=item.combo.precio
                )

            pedido.estado = "Pendiente"
            pedido.save()

            Factura.objects.create(
                pedido=pedido,
                total_pagado=pedido.total()
            )

            carrito_prod.delete()
            carrito_combo.delete()

        # 💥 ESTE ERA EL RETURN QUE FALTABA 💥
        return render(request, "ventas/pedido_confirmado.html", {
            "pedido": pedido,
            "user": usuario
        })


    except Exception as e:
        print("ERROR PEDIDO:", e)
        messages.error(request, "Ocurrió un error procesando el pedido.")
        return redirect("ventas:carrito")




# ============================================================
# ✔ PÁGINAS ESTADO
# ============================================================




# ============================================================
# 🧾 LISTA DE PEDIDOS
# ============================================================
def pedidos_cliente(request):
    usuario = get_current_usuario(request)
    if not usuario:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("usuarios:login")

    pedidos = Pedido.objects.filter(usuario=usuario).order_by("-id")
    return render(request, "ventas/pedidos.html", {"pedidos": pedidos})



# ============================================================
# 🛠 ADMIN - GESTIÓN DE PEDIDOS
# ============================================================
def admin_pedidos(request):
    usuario = get_current_usuario(request)
    if not usuario or usuario.rol != "admin":
        messages.error(request, "Acceso denegado.")
        return redirect("core:home")

    pedidos = Pedido.objects.all().order_by("-id")
    return render(request, "ventas/gestion_pedidos.html", {"pedidos": pedidos})



def actualizar_estado(request, pedido_id):
    usuario = get_current_usuario(request)
    if not usuario or usuario.rol != "admin":
        messages.error(request, "Acceso denegado.")
        return redirect("core:home")

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == "POST":
        estado = request.POST.get("estado")
        if estado:
            pedido.estado = estado
            pedido.save()
            messages.success(request, "Estado actualizado.")

    return redirect("ventas:gestion_pedidos")



# ============================================================
# 🧾 FACTURA PDF (PRODUCTOS + COMBOS)
# ============================================================
def factura_pdf(request, pedido_id):
    usuario = get_current_usuario(request)
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if not usuario or (usuario != pedido.usuario and usuario.rol != "admin"):
        messages.error(request, "Acceso denegado.")
        return redirect("core:home")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{pedido.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(70, height - 60, f"Factura #{pedido.id}")

    p.setFont("Helvetica", 12)
    p.drawString(70, height - 90, f"Cliente: {pedido.usuario.nombre_usuario}")
    p.drawString(70, height - 110, f"Fecha: {pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M')}")

    y = height - 150

    p.setFont("Helvetica-Bold", 12)
    p.drawString(70, y, "Descripción")
    p.drawString(300, y, "Cantidad")
    p.drawString(380, y, "Precio")
    p.drawString(460, y, "Subtotal")

    y -= 30
    p.setFont("Helvetica", 12)

    # Productos
    for item in pedido.items.all():
        p.drawString(70, y, item.producto.nombre[:30])
        p.drawString(300, y, str(item.cantidad))
        p.drawString(380, y, f"${item.precio}")
        p.drawString(460, y, f"${item.subtotal()}")
        y -= 20

    # Combos
    for item in pedido.items_combos.all():
        p.drawString(70, y, f"{item.combo.nombre} (Combo)")
        p.drawString(300, y, str(item.cantidad))
        p.drawString(380, y, f"${item.precio}")
        p.drawString(460, y, f"${item.subtotal()}")
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 13)
    p.drawString(70, y, f"Total: ${pedido.total()}")

    p.showPage()
    p.save()
    return response
