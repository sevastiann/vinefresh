from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Inventario para administradores
    path('inventario/', views.inventario, name='inventario'),
    path('agregar-categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('eliminar-categoria/', views.eliminar_categoria, name='eliminar_categoria'),
    path('editar-categoria/', views.editar_categoria, name='editar_categoria'),

    
    #path('sidebar/', views.sidebar, name='sidebar'),

    # Catálogo para clientes
    #path('cliente/', views.catalogo_cliente, name='catalogo_cliente'),

    # Catálogo público (sin login)
    #path('publico/', views.catalogo_publico, name='catalogo_publico'),
]
