"""
URL configuration for vinefresh project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Página principal (home y vistas públicas)
    path('', include('core.urls')),

    # Autenticación y gestión de usuarios
    path('usuarios/', include('usuarios.urls')),

    # Dashboard compartido (cliente / administrador)
    path('dashboard/', include('dashboard.urls')),

    # Módulos del sistema
    path('catalogo/', include('catalogo.urls')),   # productos + inventario
    path('ventas/', include('ventas.urls')),       # carrito, pedidos, facturas
    path('envios/', include('envios.urls')),       # seguimiento de envíos
    path('soporte/', include('soporte.urls')),     # PQRS y contacto
    path('reseñas/', include('reseñas.urls')),     # calificaciones
]

