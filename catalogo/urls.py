from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Inventario para administradores
    path('inventario/', views.inventario, name='inventario'),
    path('agregar-categoria/', views.agregar_subcategoria, name='agregar_subcategoria'),
    path('eliminar-categoria/', views.eliminar_subcategoria, name='eliminar_subcategoria'),
    path('editar-categoria/', views.editar_subcategoria, name='editar_subcategoria'),

    
    #path('sidebar/', views.sidebar, name='sidebar'),

    # Catálogo para clientes
    #path('cliente/', views.catalogo_cliente, name='catalogo_cliente'),

    # Catálogo público (sin login)
    #path('publico/', views.catalogo_publico, name='catalogo_publico'),
]
