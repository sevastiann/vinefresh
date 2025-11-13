from django.urls import path
from . import views

app_name = 'soporte'

urlpatterns = [
    path('', views.lista_soporte, name='lista_soporte'),
    path('crear/', views.crear_soporte, name='crear_soporte'),
    path('<int:soporte_id>/', views.detalle_soporte, name='detalle_soporte'),
    path('<int:soporte_id>/responder/', views.responder_soporte, name='responder_soporte'),
    path('panel-admin/', views.panel_admin_soporte, name='panel_admin_soporte'),
]
