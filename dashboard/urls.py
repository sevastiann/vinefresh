# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
]
