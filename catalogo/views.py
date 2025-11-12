from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Producto, Combo

# --------------------------
# VISTA INVENTARIO
# --------------------------
def inventario(request):
    seccion = request.GET.get('seccion', 'vinos')  # default: 'vinos'

    if seccion == 'vinos':
        productos = Producto.objects.all()
    else:  # seccion == 'combos'
        productos = Combo.objects.all()

    return render(request, 'catalogo/inventario.html', {
        'productos': productos,
        'seccion': seccion
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
# AGREGAR PRODUCTO / COMBO
# --------------------------

def agregar_producto(request):
    seccion = 'vinos'
    if request.method == 'POST':
        categorias = request.POST.getlist('categoria')
        producto = Producto(
            nombre=request.POST.get('nombre'),
            precio=request.POST.get('precio'),
            descripcion=request.POST.get('descripcion', ''),
            categoria=", ".join(categorias),
            activo=request.POST.get('activo') == 'on'
        )
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')
        producto.save()
        return HttpResponseRedirect(reverse('catalogo:inventario') + f'?seccion={seccion}')
    
    return render(request, 'catalogo/agregar_producto.html', {'seccion': seccion})


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

    # Listas para los checkboxes
    paises = ["Chile","Argentina","España","Italia","Francia","Colombia","México"]
    colores = ["Tinto","Blanco","Rosado"]
    grados = ["Menos de 10%","10% - 13%","Más de 13%"]
    uvas = ["Cabernet Sauvignon","Malbec","Merlot","Sauvignon Blanc","Verdejo","Carménère","Nebbiolo","Pinot Noir","Grenache"]
    volumenes = ["375 ml","750 ml","1 L"]

    if request.method == 'POST':
        # Obtener listas de cada categoría
        categorias_pais = request.POST.getlist('categoria_pais')
        categorias_color = request.POST.getlist('categoria_color')
        categorias_grado = request.POST.getlist('categoria_grado')
        categorias_uva = request.POST.getlist('categoria_uva')
        categorias_volumen = request.POST.getlist('categoria_volumen')

        # Guardar los datos
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.descripcion = request.POST.get('descripcion', '')
        
        # Aquí dependiendo de cómo tengas el modelo, puedes guardar las relaciones de categoría/subcategoría
        # Por simplicidad, si solo usas un campo texto:
        producto.categoria = ", ".join(categorias_pais + categorias_color + categorias_grado + categorias_uva)
        producto.subcategorias = ", ".join(categorias_volumen)

        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')

        producto.activo = request.POST.get('activo') == 'on'
        producto.save()

        return HttpResponseRedirect(reverse('catalogo:inventario') + '?seccion=vinos')

    context = {
        'producto': producto,
        'seccion': 'vinos',
        'paises': paises,
        'colores': colores,
        'grados': grados,
        'uvas': uvas,
        'volumenes': volumenes,
    }

    return render(request, 'catalogo/editar_producto.html', context)

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
