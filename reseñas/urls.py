from django.urls import path
from . import views

app_name = 'reseñas'

urlpatterns = [
    path('', views.lista_reseñas, name='lista_reseñas'),
    path('nueva/', views.nueva_reseña, name='nueva_reseña'),
    path('<int:reseña_id>/', views.detalle_reseña, name='detalle_reseña'),
]
