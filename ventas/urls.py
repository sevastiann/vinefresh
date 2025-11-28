from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    # 🛒 Carrito
    path("carrito/", views.carrito, name="carrito"),
    path("carrito/comprar/", views.pedido_crear, name="comprar"),
    path("carrito/agregar/<int:producto_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/agregar-combo/<int:combo_id>/", views.agregar_combo_al_carrito, name="agregar_combo_al_carrito"),
    path("carrito/actualizar/<int:item_id>/", views.actualizar_cantidad, name="actualizar_cantidad"),
    path("carrito/eliminar/<str:item_id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),

    # 🧾 Pedidos del cliente
    path("pedidos/", views.pedidos_cliente, name="pedidos"),
    path("factura/<int:pedido_id>/", views.factura_pdf, name="factura_pdf"),

    # 🛠 Gestión de pedidos (admin)
    path("admin/pedidos/", views.admin_pedidos, name="gestion_pedidos"),
    path("admin/pedidos/<int:pedido_id>/cambiar_estado/", views.actualizar_estado, name="actualizar_estado"),
]
