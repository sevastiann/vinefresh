from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('olvidar/', views.olvidar_contrasena_view, name='olvidar_contrasena'),
    path('restablecer/<str:token>/', views.restablecer_contrasena_view, name='restablecer_contrasena'),
]
