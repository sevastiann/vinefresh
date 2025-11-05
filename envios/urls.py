from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_envios, name='lista_envios'),
    path('<int:envio_id>/', views.detalle_envio, name='detalle_envio'),
    path('<int:envio_id>/estado/<str:nuevo_estado>/', views.cambiar_estado_envio, name='cambiar_estado_envio'),
]
