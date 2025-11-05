# usuarios/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class RedireccionRolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario está autenticado
        if request.user.is_authenticated:
            # Si intenta entrar al dashboard del rol contrario, lo redirige al correcto
            if hasattr(request.user, 'es_admin') and request.user.es_admin:
                # Evita que el admin entre al dashboard del cliente
                if request.path.startswith(reverse('dashboard_cliente')):
                    return redirect('dashboard_admin')
            else:
                # Evita que el cliente entre al dashboard del admin
                if request.path.startswith(reverse('dashboard_admin')):
                    return redirect('dashboard_cliente')

        # Continua con la petición normal
        response = self.get_response(request)
        return response
