from django.urls import path
from . import views

app_name = 'ventas'  # 👈 Para usar namespacing (ventas:carrito_html, etc.)

urlpatterns = [

    # -------------------------
    # PÁGINAS HTML PRINCIPALES
    # -------------------------
    #path("", views.ventas_home, name="ventas_home"),
    path("carrito/", views.carrito, name="carrito"),
    #path("pedidos/", views.pedidos, name="pedidos"),
    #path("pedidos/crear/", views.pedido_crear, name="pedido_crear"),
    #path("facturas/", views.facturas, name="facturas_html"),
    #path("facturas/crear/", views.factura_crear, name="factura_crear"),
    #path("cupones/", views.cupones, name="cupones"),
    #path("cupones/crear/", views.cupones_crear, name="cupones_crear"),

     # -------------------------
     # API: CARRITO
     # -------------------------
    path('api/carrito/agregar/<int:producto_id>/<int:cantidad>/',
         views.agregar_al_carrito,
         name='agregar_al_carrito'),

    ## -------------------------
    ## API: PEDIDOS
    ## -------------------------
    #path(
    #    "api/pedidos/crear/<int:carrito_id>/<str:precio>/",
    #    views.crear_pedido,
    #    name="crear_pedido"
    #),
    #path(
    #    "api/pedidos/ver/<int:usuario_id>/",
    #    views.ver_pedidos,
    #    name="ver_pedidos"
    #),
#
    ## -------------------------
    ## API: FACTURAS
    ## -------------------------
    #path(
    #    "api/facturas/crear/<int:usuario_id>/<str:metodo_pago>/",
    #    views.crear_factura,
    #    name="crear_factura"
    #),
#
    ## -------------------------
    ## API: CUPONES
    ## -------------------------
    #path(
    #    "api/cupon/validar/<str:codigo>/",
    #    views.validar_cupon,
    #    name="validar_cupon"
    #),
]
