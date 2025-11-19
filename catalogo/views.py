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
        categorias = request.POST.getlist('categoria')
        combo = Combo(
            nombre=request.POST.get('nombre'),
            precio=request.POST.get('precio'),
            descripcion=request.POST.get('descripcion', ''),
            categoria=", ".join(categorias),
            activo=request.POST.get('activo') == 'on'
        )
        if request.FILES.get('imagen'):
            combo.imagen = request.FILES.get('imagen')
        combo.save()
        return HttpResponseRedirect(reverse('catalogo:inventario') + f'?seccion={seccion}')
    
    return render(request, 'catalogo/agregar_combo.html', {'seccion': seccion})

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

    # Listas para checkboxes
    festividades = ["Navidad", "Año Nuevo", "San Valentín", "Día del Padre", "Día de la Madre"]
    premium = ["Gold", "Platinum", "Black Label"]
    regalo = ["Amistad", "Cumpleaños", "Pareja", "Corporativo"]

    if request.method == 'POST':
        categorias = request.POST.getlist('categoria')
        combo.nombre = request.POST.get('nombre')
        combo.precio = request.POST.get('precio')
        combo.descripcion = request.POST.get('descripcion', '')
        combo.categoria = ", ".join(categorias)
        combo.unidades = request.POST.get('unidades', 1)

        if request.FILES.get('imagen'):
            combo.imagen = request.FILES.get('imagen')

        combo.activo = request.POST.get('activo') == 'on'
        combo.save()
        return HttpResponseRedirect(reverse('catalogo:inventario') + '?seccion=combos')

    context = {
        'combo': combo,
        'seccion': 'combos',
        'festividades': festividades,
        'premium': [f"premium_{p.lower()}" for p in premium],
        'regalo': [f"regalo_{r.lower()}" for r in regalo],
    }

    return render(request, 'catalogo/editar_combo.html', context)


# --------------------------
# ELIMINAR PRODUCTO/COMBO
# --------------------------
def eliminar_producto(request, producto_id):
    get_object_or_404(Producto, id=producto_id).delete()
    return HttpResponseRedirect(reverse('catalogo:inventario') + '?seccion=vinos')

def eliminar_combo(request, combo_id):
    get_object_or_404(Combo, id=combo_id).delete()
    return HttpResponseRedirect(reverse('catalogo:inventario') + '?seccion=combos')

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
        productos = Combo.objects.all()
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
    seccion = request.GET.get('seccion', 'vinos')
    if seccion == 'combos':
        productos = Combo.objects.filter(activo=True)
    else:
        productos = Producto.objects.filter(activo=True)
    return render(request, 'catalogo/productos.html', {
        'productos': productos,
        'seccion': seccion,
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



