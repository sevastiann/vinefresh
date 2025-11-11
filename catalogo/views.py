# catalogo/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Producto, Subcategoria, Combo, Categoria

# -----------------------------
# 🔹 Catálogo general para clientes
# -----------------------------
def lista_productos(request):
    productos = Producto.objects.all()

    # --- FILTROS ---
    pais = request.GET.get('pais')
    color = request.GET.get('color')
    dulzura = request.GET.get('dulzura')
    cuerpo = request.GET.get('cuerpo')

    if pais:
        productos = productos.filter(pais_origen__icontains=pais)
    if color:
        productos = productos.filter(subcategoria__nombre__icontains=color)
    if dulzura:
        productos = productos.filter(subcategoria__nombre__icontains=dulzura)
    if cuerpo:
        productos = productos.filter(subcategoria__nombre__icontains=cuerpo)

    # --- PAGINACIÓN ---
    paginator = Paginator(productos, 9)
    page_number = request.GET.get('page')
    productos_pagina = paginator.get_page(page_number)

    return render(request, 'catalogo/catalogo.html', {
        'productos': productos_pagina
    })

# -----------------------------
# 🔹 Detalle de producto individual
# -----------------------------
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'catalogo/detalle.html', {'producto': producto})

# -----------------------------
# 🔹 Inventario (admin)
# -----------------------------
def inventario(request):
    # --- Control de acceso ---
    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')
    if request.session.get('usuario_rol') != 'admin':
        return redirect('catalogo:catalogo_cliente')

    # --- Sección actual (productos / combos) ---
    seccion_actual = request.GET.get('seccion', 'productos')

    # --- Subcategorías filtradas por sección ---
    subcategorias_productos = Subcategoria.objects.filter(seccion='productos')
    subcategorias_combos = Subcategoria.objects.filter(seccion='combos')

    # --- JSON para modales / scripts ---
    categorias_json = {
        "productos": list(
            Categoria.objects.filter(subcategorias__seccion='productos')
            .values('id', 'nombre')
            .distinct()
        ),
        "combos": list(
            Categoria.objects.filter(subcategorias__seccion='combos')
            .values('id', 'nombre')
            .distinct()
        ),
    }

    # --- Diccionario de categorías estáticas desde el modelo ---
    categorias_estaticas = Subcategoria.CATEGORIAS_PRINCIPALES

    return render(request, 'catalogo/inventario.html', {
        'seccion': seccion_actual,
        'categorias_json': json.dumps(categorias_json),
        'categorias': Categoria.objects.all(),
        'subcategorias': Subcategoria.objects.all(),
        'categorias_estaticas': categorias_estaticas,
        'subcategorias_productos': subcategorias_productos,
        'subcategorias_combos': subcategorias_combos,
    })

# -----------------------------
# 🔹 Catálogo público (visitantes)
# -----------------------------
def catalogo_publico(request):
    return render(request, 'catalogo/catalogo_publico.html')

# -----------------------------
# 🔹 Catálogo del cliente logueado
# -----------------------------
def catalogo_cliente(request):
    return render(request, 'catalogo/catalogo_cliente.html')

# -----------------------------
# 🔹 Agregar nueva subcategoría
# -----------------------------
def agregar_subcategoria(request):
    if request.method == 'POST':
        seccion = request.POST.get('seccion')
        categoria_principal = request.POST.get('categoria_principal')  # CORREGIDO: debe coincidir con el name del formulario
        nombre_subcategoria = request.POST.get('nombre')

        if not (seccion and categoria_principal and nombre_subcategoria):
            messages.error(request, '⚠️ Todos los campos son obligatorios.')
            return redirect('catalogo:inventario')

        Subcategoria.objects.create(
            seccion=seccion,
            categoria_principal=categoria_principal,
            nombre=nombre_subcategoria
        )
        messages.success(request, '✅ Subcategoría agregada correctamente.')
        return redirect('catalogo:inventario')

# -----------------------------
# 🔹 Eliminar subcategoría
# -----------------------------
def eliminar_subcategoria(request):
    if request.method == 'POST':
        subcategoria_id = request.POST.get('categoria_id')
        try:
            subcategoria = Subcategoria.objects.get(id=subcategoria_id)
            subcategoria.delete()
            messages.success(request, '🗑️ Subcategoría eliminada correctamente.')
        except Subcategoria.DoesNotExist:
            messages.error(request, '⚠️ La subcategoría no existe.')
        return redirect('catalogo:inventario')

    # Si se entra por GET (no recomendado)
    subcategorias = Subcategoria.objects.all()
    return render(request, 'catalogo/inventario.html', {'subcategorias': subcategorias})

# -----------------------------
# 🔹 Editar subcategoría
# -----------------------------
def editar_subcategoria(request):
    if request.method == 'POST':
        subcategoria_id = request.POST.get('categoria_id')
        nuevo_nombre = request.POST.get('nuevo_nombre')
        nueva_seccion = request.POST.get('seccion')

        subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
        subcategoria.nombre = nuevo_nombre
        subcategoria.seccion = nueva_seccion
        subcategoria.save()

        messages.success(request, '✅ Subcategoría actualizada correctamente.')
        return redirect('catalogo:inventario')
