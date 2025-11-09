from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Producto


def lista_productos(request):
    # --- FILTROS ---
    productos = Producto.objects.all()

    pais = request.GET.get('pais')
    color = request.GET.get('color')
    dulzura = request.GET.get('dulzura')
    cuerpo = request.GET.get('cuerpo')

    if pais:
        productos = productos.filter(pais_origen__icontains=pais)

    if color:
        productos = productos.filter(categoria__color__icontains=color)

    if dulzura:
        productos = productos.filter(categoria__azucar__icontains=dulzura)

    if cuerpo:
        productos = productos.filter(categoria__gas_carbonico__icontains=cuerpo)

    # --- PAGINACIÓN ---
    paginator = Paginator(productos, 9)  # 9 productos por página
    page_number = request.GET.get('page')
    productos_pagina = paginator.get_page(page_number)

    # --- MANDAR A TEMPLATE ---
    return render(request, 'catalogo/catalogo.html', {
        'productos': productos_pagina
    })


def detalle_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    return render(request, 'catalogo/detalle.html', {
        'producto': producto
    })
