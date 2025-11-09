from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [

    # -----------------------------
    # CARRITO
    # -----------------------------
    path('carrito/<int:usuario_id>/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:usuario_id>/<int:producto_id>/<int:cantidad>/', views.agregar_al_carrito, name='agregar_al_carrito'),

    # -----------------------------
    # FACTURAS
    # -----------------------------
    path('factura/crear/<int:usuario_id>/<str:metodo_pago>/', views.crear_factura, name='crear_factura'),

    # -----------------------------
    # CUPONES
    # -----------------------------
    path('cupon/<str:codigo>/', views.validar_cupon, name='validar_cupon'),

    # -----------------------------
    # PEDIDOS
    # -----------------------------
    path('pedido/crear/<int:carrito_id>/<str:precio>/', views.crear_pedido, name='crear_pedido'),
    path('pedido/usuario/<int:usuario_id>/', views.ver_pedidos, name='ver_pedidos'),

    # -----------------------------
    # FAVORITOS
    # -----------------------------
    path('favoritos/', views.favoritos, name='favoritos'),
    path('favoritos/agregar/<int:usuario_id>/<int:producto_id>/', views.agregar_favorito, name='agregar_favorito'),
]
