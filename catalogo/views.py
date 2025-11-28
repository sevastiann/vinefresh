from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Producto, Combo
from django.contrib import messages


# --------------------------
# AGREGAR PRODUCTO / COMBO
# --------------------------
def agregar_producto(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        precio = request.POST.get("precio")
        descripcion = request.POST.get("descripcion", "")

        # Campos de filtro
        pais_origen = request.POST.get("pais_origen", "")
        categoria = request.POST.get("categoria", "")  # Color
        grado_alcohol = request.POST.get("grado_alcohol", "")
        tipo_fruto = request.POST.get("tipo_fruto", "")
        subcategoria = request.POST.get("subcategoria", "")

        imagen = request.FILES.get("imagen")

        # Validación básica
        if not nombre or not precio:
            messages.error(request, "El nombre y el precio son obligatorios.")
            return redirect("catalogo:agregar_producto")

        # Crear producto
        producto = Producto(
            nombre=nombre,
            precio=precio,
            descripcion=descripcion,
            pais_origen=pais_origen,
            categoria=categoria,
            grado_alcohol=grado_alcohol if grado_alcohol else None,
            tipo_fruto=tipo_fruto,
            subcategoria=subcategoria,
            activo=True
        )

        if imagen:
            producto.imagen = imagen

        producto.save()

        messages.success(request, "Producto agregado correctamente.")
        return redirect("catalogo:inventario")  # Ajusta según tu URL real

    return render(request, "catalogo/agregar_producto.html")



def agregar_combo(request):
    seccion = 'combos'

    if request.method == 'POST':

        categorias = request.POST.getlist('categoria')  # si decides usar categorías futuras

        festividades = request.POST.getlist("fest")
        premium = request.POST.getlist("prem")
        regalo = request.POST.getlist("reg")

        combo = Combo(
            nombre=request.POST.get('nombre'),
            precio=request.POST.get('precio'),
            descripcion=request.POST.get('descripcion', ''),

            # 🔥 IMPORTANTÍSIMO
            categoria=", ".join(categorias),
            subcategoria=request.POST.get('subcategoria', ''),

            unidades=request.POST.get('unidades', 1),

            festividad=", ".join(festividades),
            premium=", ".join(premium),
            regalo=", ".join(regalo),

            activo=request.POST.get('activo') == 'on'
        )

        if request.FILES.get('imagen'):
            combo.imagen = request.FILES.get('imagen')

        combo.save()

        return HttpResponseRedirect(reverse('catalogo:inventario') + "?seccion=combos")

    return render(request, 'catalogo/agregar_combo.html', {'seccion': 'combos'})


# --------------------------
# EDITAR PRODUCTO/COMBO
# --------------------------
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # 🔥 Listas para selects (país, color, alcohol, uva, volumen)
    PAISES = ["Chile", "Argentina", "España", "Italia", "Francia", "Colombia", "México"]
    COLORES = ["Tinto", "Blanco", "Rosado"]
    ALCOHOLES = ["Menos de 10%", "10% - 13%", "Más de 13%"]
    UVAS = [
        "Cabernet Sauvignon", "Malbec", "Merlot", "Sauvignon Blanc",
        "Verdejo", "Carménère", "Nebbiolo", "Pinot Noir", "Grenache"
    ]
    VOLUMENES = ["375 ml", "750 ml", "1 L"]

    if request.method == "POST":
        producto.nombre = request.POST.get("nombre")
        producto.precio = request.POST.get("precio")
        producto.descripcion = request.POST.get("descripcion", "")

        # 🔹 Filtros (coinciden con los del catálogo)
        producto.pais_origen = request.POST.get("pais_origen", "")
        producto.categoria = request.POST.get("categoria", "")  # Color
        producto.grado_alcohol = request.POST.get("grado_alcohol") or None
        producto.tipo_fruto = request.POST.get("tipo_fruto", "")
        producto.subcategoria = request.POST.get("subcategoria", "")

        # Imagen nueva
        imagen_nueva = request.FILES.get("imagen")
        if imagen_nueva:
            producto.imagen = imagen_nueva

        producto.save()
        messages.success(request, "Producto actualizado correctamente.")
        return redirect("catalogo:inventario")

    return render(request, "catalogo/editar_producto.html", {
        "producto": producto,

        # 🔥 Enviar listas para el formulario
        "paises": PAISES,
        "colores": COLORES,
        "alcoholes": ALCOHOLES,
        "uvas": UVAS,
        "volumenes": VOLUMENES,
    })


def editar_combo(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id)

    # Listas de opciones para los checkboxes
    festividades = ["Navidad", "Año Nuevo", "San Valentín", "Día del Padre", "Día de la Madre"]
    premium = ["premium_gold", "premium_platinum", "premium_black_label"]
    regalo = ["regalo_amistad", "regalo_cumpleaños", "regalo_pareja", "regalo_corporativo"]

    if request.method == "POST":

        combo.nombre = request.POST.get("nombre")
        combo.precio = request.POST.get("precio")
        combo.descripcion = request.POST.get("descripcion", "")

        # Festividades seleccionadas
        fest_list = request.POST.getlist("fest")
        combo.festividad = ", ".join(fest_list) if fest_list else ""

        # Premium seleccionadas
        prem_list = request.POST.getlist("prem")
        combo.premium = ", ".join(prem_list) if prem_list else ""

        # Regalos seleccionados
        reg_list = request.POST.getlist("reg")
        combo.regalo = ", ".join(reg_list) if reg_list else ""

        # Actualizar imagen si se sube una nueva
        imagen_nueva = request.FILES.get("imagen")
        if imagen_nueva:
            combo.imagen = imagen_nueva

        # Activación / desactivación del combo
        combo.activo = request.POST.get("activo") == "on"

        combo.save()

        from django.urls import reverse
        return redirect(f"{reverse('catalogo:inventario')}?seccion=combos")

    # Pasar las opciones y estado actual para marcar los checkboxes
    context = {
        "combo": combo,
        "seccion": "combos",
        "festividades": festividades,
        "premium": premium,
        "regalo": regalo,

        "fest_selected": combo.festividad.split(", ") if combo.festividad else [],
        "premium_selected": combo.premium.split(", ") if combo.premium else [],
        "reg_selected": combo.regalo.split(", ") if combo.regalo else [],
    }

    return render(request, "catalogo/editar_combo.html", context)



# --------------------------
# ELIMINAR PRODUCTO/COMBO
# --------------------------
def eliminar_producto(request, producto_id):
    get_object_or_404(Producto, id=producto_id).delete()
    return HttpResponseRedirect(reverse('catalogo:inventario') + '?seccion=vinos')

def eliminar_combo(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id)
    combo.activo = False
    combo.save()

    return HttpResponseRedirect(reverse("catalogo:inventario") + "?seccion=combos")


# --------------------------
# DETALLE PRODUCTO/COMBO
# --------------------------
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'catalogo/modal_detalle.html', {'producto': producto})

def detalle_combo(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id)
    return render(request, 'catalogo/modal_detalle.html', {'producto': combo})


from django.shortcuts import render, get_object_or_404
from .models import Producto, Combo

# --------------------------
# Vista de inventario (Admin)
# --------------------------
def inventario(request):
    seccion = request.GET.get('seccion', 'vinos')
    if seccion == 'combos':
        productos = Combo.objects.filter(activo=True)
    else:
        productos = Producto.objects.all()
    return render(request, 'catalogo/inventario.html', {
        'productos': productos,
        'seccion': seccion,
    })

# --------------------------
# Vista de productos (Cliente)
# --------------------------
def productos(request):
    seccion = request.GET.get("seccion", "vinos")

    if seccion == "combos":
        productos_qs = Combo.objects.filter(activo=True)
    else:
        # No reasignes seccion, ya viene como "vinos" por defecto
        productos_qs = Producto.objects.filter(activo=True)

    return render(request, "catalogo/productos.html", {
        "productos": productos_qs,
        "seccion": seccion,
    })


# --------------------------
# Detalle Producto/Combo
# --------------------------
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, 'catalogo/detalle_producto.html', {'producto': producto})

def detalle_combo(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id, activo=True)
    return render(request, 'catalogo/detalle_combo.html', {'combo': combo})

from django.db.models import Q
from django.shortcuts import render
from .models import Producto

def filtrar_productos(request):
    productos = Producto.objects.filter(activo=True)

    # --------------------------------
    # 🔍 BUSCAR
    # --------------------------------
    buscar = request.GET.get("buscar")
    if buscar:
        productos = productos.filter(nombre__icontains=buscar)

    # --------------------------------
    # 💰 PRECIO
    # --------------------------------
    pmin = request.GET.get("precio_min")
    pmax = request.GET.get("precio_max")

    if pmin and pmin.isdigit():
        productos = productos.filter(precio__gte=float(pmin))

    if pmax and pmax.isdigit():
        productos = productos.filter(precio__lte=float(pmax))

    # --------------------------------
    # 🌍 PAÍSES
    # --------------------------------
    paises = request.GET.get("pais")
    if paises:
        lista = paises.split(",")
        productos = productos.filter(pais_origen__in=lista)

    # --------------------------------
    # 🎨 COLOR (categoría)
    # --------------------------------
    colores = request.GET.get("color")
    if colores:
        lista = colores.split(",")
        productos = productos.filter(categoria__in=lista)

    # --------------------------------
    # 🍇 TIPO DE UVA (tipo_fruto)
    # --------------------------------
    uvas = request.GET.get("uva")
    if uvas:
        lista = uvas.split(",")
        productos = productos.filter(tipo_fruto__in=lista)

    # --------------------------------
    # 🔥 GRADO DE ALCOHOL
    # --------------------------------
    alcohol = request.GET.get("alcohol")
    if alcohol:
        lista = alcohol.split(",")
        q = Q()
        for val in lista:
            if val == "Menos de 10%":
                q |= Q(grado_alcohol__lt=10)
            elif val == "10%-13%":
                q |= Q(grado_alcohol__gte=10, grado_alcohol__lte=13)
            elif val == "Más de 13%":
                q |= Q(grado_alcohol__gt=13)
        productos = productos.filter(q)

    # --------------------------------
    # 🧪 VOLÚMENES
    # --------------------------------
    vol = request.GET.get("vol")
    if vol:
        lista = vol.split(",")
        productos = productos.filter(subcategoria__in=lista)

    productos = productos.distinct()

    return render(request, "catalogo/productos_grid.html", {
        "productos": productos,
        "seccion": "vinos",
    })

def filtrar_inventarios(request):
    productos = Producto.objects.all()

    # BUSCAR
    buscar = request.GET.get("buscar")
    if buscar:
        productos = productos.filter(nombre__icontains=buscar)

    # PRECIO
    pmin = request.GET.get("precio_min")
    pmax = request.GET.get("precio_max")

    if pmin and pmin.isdigit():
        productos = productos.filter(precio__gte=float(pmin))

    if pmax and pmax.isdigit():
        productos = productos.filter(precio__lte=float(pmax))

    # PAÍS
    paises = request.GET.get("pais")
    if paises:
        lista = paises.split(",")
        productos = productos.filter(pais_origen__in=lista)

    # COLOR
    colores = request.GET.get("color")
    if colores:
        lista = colores.split(",")
        productos = productos.filter(categoria__in=lista)

    # UVA
    uvas = request.GET.get("uva")
    if uvas:
        lista = uvas.split(",")
        productos = productos.filter(tipo_fruto__in=lista)

    # ALCOHOL
    alcohol = request.GET.get("alcohol")
    if alcohol:
        lista = alcohol.split(",")
        q = Q()
        for val in lista:
            if val == "Menos de 10%":
                q |= Q(grado_alcohol__lt=10)
            elif val == "10%-13%":
                q |= Q(grado_alcohol__gte=10, grado_alcohol__lte=13)
            elif val == "Más de 13%":
                q |= Q(grado_alcohol__gt=13)
        productos = productos.filter(q)

    # VOLUMEN
    vol = request.GET.get("vol")
    if vol:
        lista = vol.split(",")
        productos = productos.filter(subcategoria__in=lista)

    productos = productos.distinct()

    return render(request, "catalogo/inventarios_grid.html", {
        "productos": productos,
        "seccion": "vinos",
    })

def filtrar_combos(request):
    combos = Combo.objects.filter(activo=True)

    # BUSCAR
    buscar = request.GET.get("buscar", "").strip()
    if buscar:
        combos = combos.filter(nombre__icontains=buscar)

    # PRECIO
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")

    if precio_min:
        combos = combos.filter(precio__gte=precio_min)
    if precio_max:
        combos = combos.filter(precio__lte=precio_max)

    # FESTIVIDAD
    fest = request.GET.get("fest")
    if fest:
        combos = combos.filter(festividad__in=fest.split(","))

    # PREMIUM
    prem = request.GET.get("prem")
    if prem:
        combos = combos.filter(premium__in=prem.split(","))

    # REGALO
    reg = request.GET.get("reg")
    if reg:
        combos = combos.filter(regalo__in=reg.split(","))

    # RETORNAR PARCIAL
    return render(request, "catalogo/combos_grid.html", {
        "combos": combos
    })

def filtrar_combos_cliente(request):
    combos = Combo.objects.filter(activo=True)

    # Buscar
    buscar = request.GET.get("buscar")
    if buscar:
        combos = combos.filter(nombre__icontains=buscar)

    # Precio
    pmin = request.GET.get("precio_min")
    pmax = request.GET.get("precio_max")
    if pmin:
        combos = combos.filter(precio__gte=pmin)
    if pmax:
        combos = combos.filter(precio__lte=pmax)

    # Filtros
    for campo in ["festividad", "premium", "regalo"]:
        valores = request.GET.get(campo[:4])  # fest, prem, reg
        if valores:
            combos = combos.filter(**{f"{campo}__in": valores.split(",")})

    return render(request, "catalogo/grids/combos_cliente_grid.html", {
        "combos": combos
    })

def agregar_combo_al_carrito(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id)
    usuario = get_current_usuario(request)

    if usuario:
        carrito_obj, creado = CarritoCombo.objects.get_or_create(
            usuario=usuario,
            combo=combo,
            defaults={"cantidad": 1}
        )
        if not creado:
            carrito_obj.cantidad += 1
            carrito_obj.save()
    else:
        carrito_sesion = request.session.get("carrito_combos", {})
        cid = str(combo.id)
        carrito_sesion[cid] = carrito_sesion.get(cid, 0) + 1
        request.session["carrito_combos"] = carrito_sesion

    return redirect("ventas:carrito")
