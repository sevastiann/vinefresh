from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    # 🛒 Ver carrito
    path("carrito/", views.carrito, name="carrito"),

    # ➕ Agregar al carrito (solo producto_id)
    path("carrito/agregar/<int:producto_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),

    # 🔄 Actualizar cantidad de un item (solo item_id)
    path("carrito/actualizar/<int:item_id>/", views.actualizar_cantidad, name="actualizar_cantidad"),

    # ❌ Eliminar producto del carrito
    path("carrito/eliminar/<int:item_id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
]
