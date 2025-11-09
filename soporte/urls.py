from django.urls import path
from . import views

app_name = 'soporte'

urlpatterns = [
    path('', views.lista_soporte, name='lista_soporte'),
    path('crear/', views.crear_soporte, name='crear_soporte'),
    path('<int:soporte_id>/', views.detalle_soporte, name='detalle_soporte'),
    path('<int:soporte_id>/estado/<str:nuevo_estado>/', views.cambiar_estado_soporte, name='cambiar_estado_soporte'),
]
