from django.urls import path
from . import views

urlpatterns = [

    # -------------------------
    # CARRITO
    # -------------------------
    path("carrito/agregar/<int:usuario_id>/<int:producto_id>/<int:cantidad>/",
         views.agregar_al_carrito, name="agregar_al_carrito"),

    path("carrito/ver/<int:usuario_id>/",
         views.ver_carrito, name="ver_carrito"),


    # -------------------------
    # PEDIDOS (API)
    # -------------------------
    path("pedidos/crear/<int:carrito_id>/<str:precio>/",
         views.crear_pedido, name="crear_pedido"),

    path("pedidos/ver/<int:usuario_id>/",
         views.ver_pedidos, name="ver_pedidos"),


    # -------------------------
    # PEDIDOS (HTML)
    # -------------------------
    path("pedidos/", views.ventas_pedidos, name="ventas_pedidos_html"),
    path("pedidos/crear/", views.ventas_pedido_crear, name="ventas_pedido_crear"),


    # -------------------------
    # FACTURAS (API)
    # -------------------------
    path("facturas/crear/<int:usuario_id>/<str:metodo_pago>/",
         views.crear_factura, name="crear_factura"),


    # -------------------------
    # FACTURAS (HTML)
    # -------------------------
    path("facturas/", views.ventas_facturas, name="ventas_facturas_html"),
    path("facturas/crear/", views.ventas_factura_crear, name="ventas_factura_crear"),


    # -------------------------
    # CUPONES (API)
    # -------------------------
    path("cupon/validar/<str:codigo>/",
         views.validar_cupon, name="validar_cupon"),


    # -------------------------
    # CUPONES (HTML)
    # -------------------------
    path("cupones/", views.ventas_cupones, name="ventas_cupones_html"),
    path("cupones/crear/", views.ventas_cupones_crear, name="ventas_cupones_crear"),


    # -------------------------
    # PÁGINAS HTML PRINCIPALES
    # -------------------------
    path("", views.ventas_home, name="ventas_home"),
    path("carrito/", views.ventas_carrito, name="ventas_carrito_html"),
]
