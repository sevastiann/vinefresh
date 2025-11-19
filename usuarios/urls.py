from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),

    # Recuperación de contraseña
    path('olvidar-contrasena/', views.olvidar_contrasena_view, name='olvidar_contrasena'),
    path('restablecer-contrasena/<str:token>/', views.restablecer_contrasena_view, name='restablecer_contrasena'),

    # Gestión de usuarios
    path('enviar-invitacion/', views.enviar_invitacion_view, name='enviar_invitacion'),
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('detalle-cliente/<int:id>/', views.detalle_cliente, name='detalle_cliente'),

    # Activar / Desactivar usuario
    path('cambiar_estado/<int:usuario_id>/', views.cambiar_estado, name='cambiar_estado'),
    path('aceptar-invitacion/<str:token>/', views.registro_admin_invitado_view, name='registro_admin_invitado'),
    path('registro-exitoso/', views.registro_exitoso_view, name='registro_exitoso'),

    # Configuración de perfil
    path('perfil/configuracion/', views.configuracion_perfil, name='configuracion_perfil'),

]
