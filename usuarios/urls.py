from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),

    # Recuperación de contraseña
    path('olvidar-contrasena/', views.olvidar_contrasena_view, name='olvidar_contrasena'),
    path('restablecer-contrasena/<str:token>/', views.restablecer_contrasena_view, name='restablecer_contrasena'),

    # Gestión de usuarios
    path('usuarios-dropdown/', views.usuarios_dropdown, name='usuarios_dropdown'),
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('eliminar-usuario/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('detalle-cliente/<int:id>/', views.detalle_cliente, name='detalle_cliente'),

]
