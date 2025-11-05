from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_admin, name='perfil_admin'),
    path('configuracion/', views.configuracion, name='configuracion_admin'),
]
