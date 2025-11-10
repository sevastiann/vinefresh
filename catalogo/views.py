# catalogo/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Producto, Subcategoria, Combo
from django.http import JsonResponse
import json

# -----------------------------
# 🔹 Catálogo general (para clientes)
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
# 🔹 Inventario (para admin)
# -----------------------------
def inventario(request):
    # Control de acceso: solo admins
    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')

    if request.session.get('usuario_rol') != 'admin':
        return redirect('catalogo:catalogo_cliente')

    # ✅ Ahora usamos Subcategoria, no Categoria
    subcategorias_productos = Subcategoria.objects.filter(seccion='productos')
    subcategorias_combos = Subcategoria.objects.filter(seccion='combos')

    categorias_json = {
        "productos": list(subcategorias_productos.values('id', 'categoria_principal', 'nombre')),
        "combos": list(subcategorias_combos.values('id', 'categoria_principal', 'nombre')),
    }

    return render(request, 'catalogo/inventario.html', {
        'seccion': request.GET.get('seccion', 'productos'),
        'categorias': Subcategoria.objects.all(),
        'categorias_json': json.dumps(categorias_json)
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
def agregar_categoria(request):
    if request.method == 'POST':
        seccion = request.POST.get('seccion')
        categoria_principal = request.POST.get('categoria')
        nombre_subcategoria = request.POST.get('subcategoria')

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
def eliminar_categoria(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        try:
            subcategoria = Subcategoria.objects.get(id=categoria_id)
            subcategoria.delete()
            messages.success(request, '🗑️ Subcategoría eliminada correctamente.')
        except Subcategoria.DoesNotExist:
            messages.error(request, '⚠️ La subcategoría no existe.')

        return redirect('catalogo:inventario')

    # Si se entra por GET
    subcategorias = Subcategoria.objects.all()
    return render(request, 'catalogo/inventario.html', {'categorias': subcategorias})

# -----------------------------
# 🔹 Editar subcategoría
# -----------------------------
def editar_categoria(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        nuevo_nombre = request.POST.get('nuevo_nombre')
        nueva_seccion = request.POST.get('seccion')

        subcategoria = get_object_or_404(Subcategoria, id=categoria_id)
        subcategoria.nombre = nuevo_nombre
        subcategoria.seccion = nueva_seccion
        subcategoria.save()

        messages.success(request, '✅ Subcategoría actualizada correctamente.')
        return redirect('catalogo:inventario')