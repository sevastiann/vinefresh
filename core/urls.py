from django.urls import path
from . import views

app_name = 'core'  # 👈 agrega esto

urlpatterns = [
    path('', views.home, name='home'),
    path('contacto/', views.contacto, name='contacto'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('terminos/', views.terminos, name='terminos'),
]
