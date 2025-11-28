from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    
    # 🧩 Inventario para administradores
    path('inventario/', views.inventario, name='inventario'),
    path('productos/', views.productos, name='productos'),
    path("filtrar_productos/", views.filtrar_productos, name="filtrar_productos"),
    path("filtrar_inventarios/", views.filtrar_inventarios, name="filtrar_inventarios"),


    # 🍷 Vinos / Productos
    path('vinos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:producto_id>/detalle/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

    # 🎁 Combos
    path('combos/agregar/', views.agregar_combo, name='agregar_combo'),
    path('combos/<int:combo_id>/editar/', views.editar_combo, name='editar_combo'),
    path('combos/<int:combo_id>/detalle/', views.detalle_combo, name='detalle_combo'),
    path('combos/<int:combo_id>/eliminar/', views.eliminar_combo, name='eliminar_combo'),
    path("filtrar-combos/", views.filtrar_combos, name="filtrar_combos"),
    path("filtrar-combos-cliente/", views.filtrar_combos_cliente, name="filtrar_combos_cliente"),
]
