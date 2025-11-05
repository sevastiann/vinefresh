from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_reseñas, name='lista_reseñas'),
    path('<int:reseña_id>/', views.detalle_reseña, name='detalle_reseña'),
    path('crear/<int:producto_id>/<int:usuario_id>/<int:calificacion>/', views.crear_reseña, name='crear_reseña'),
]
