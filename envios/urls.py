from django.urls import path
from . import views

urlpatterns = [
    path("listar/", views.envios_listar, name="envios_listar"),
    path("detalle/<int:envio_id>/", views.envios_detalle, name="envios_detalle"),
    path("crear/", views.envios_crear, name="envios_crear"),
    path("editar/<int:envio_id>/", views.envios_editar, name="envios_editar"),
    path("eliminar/<int:envio_id>/", views.envios_eliminar, name="envios_eliminar"),

    path("seguimiento/<int:envio_id>/", views.seguimiento, name="seguimiento"),
    path("rutas/<int:envio_id>/", views.rutas, name="rutas"),

    path("transportadores/", views.transportadores, name="transportadores"),
]
