from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from .models import Usuario
from datetime import datetime
import re

# -------------------------
# LOGIN
# -------------------------
def usuario_logueado(request):
    """Verifica si hay un usuario logueado en la sesión"""
    return 'usuario_id' in request.session

def home_view(request):
    if usuario_logueado(request):
        nombre = request.session['usuario_nombre']
        return render(request, 'core/home.html', {'nombre': nombre})
    else:
        return redirect('login')

def login_view(request):
    mensaje = ''
    if request.method == 'POST':
        email = request.POST.get('usuario')  # El campo en el form sigue llamándose 'usuario'
        clave = request.POST.get('password')

        if not email or not clave:
            mensaje = 'Por favor completa todos los campos.'
        else:
            # Buscar usuario solo por correo
            user = Usuario.objects.filter(email=email).first()

            if user and check_password(clave, user.password):
                # Guardamos los datos del usuario en la sesión
                request.session['usuario_id'] = user.id
                request.session['usuario_nombre'] = user.nombre_usuario
                request.session['usuario_rol'] = getattr(user, 'rol', 'cliente')  # Por si no existiera rol

                # Redirigir según rol
                if user.rol == 'admin':
                    return redirect('dashboard_admin')
                else:
                    return redirect('dashboard_cliente')
            else:
                mensaje = 'Correo o contraseña incorrectos.'

    return render(request, 'usuarios/login.html', {'mensaje': mensaje})

# -------------------------
# REGISTRO
# -------------------------
def validar_email(email):
    dominios_permitidos = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return False, "Formato de email inválido"
    if email.split('@')[1] not in dominios_permitidos:
        return False, "Dominio no permitido"
    return True, "Email válido"

def calcular_edad(fecha_nacimiento):
    try:
        hoy = datetime.now().date()
        fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad
    except:
        return None

def registro_view(request):
    if request.method == 'GET':
        return render(request, 'usuarios/registro.html')

    if request.method == 'POST':
        datos = request.POST
        campos = ['nombre', 'apellido', 'fecha_nacimiento', 'email', 'telefono', 'pais', 'nombre_usuario', 'password']
        for campo in campos:
            if not datos.get(campo):
                return JsonResponse({'success': False, 'error': f'Campo {campo} requerido'}, status=400)

        email_ok, msg_email = validar_email(datos['email'])
        if not email_ok:
            return JsonResponse({'success': False, 'error': msg_email}, status=400)

        edad = calcular_edad(datos['fecha_nacimiento'])
        if edad is None or edad < 18:
            return JsonResponse({'success': False, 'error': 'Debes ser mayor de 18 años'}, status=400)

        if Usuario.objects.filter(email=datos['email']).exists():
            return JsonResponse({'success': False, 'error': 'Email ya registrado'}, status=400)
        if Usuario.objects.filter(nombre_usuario=datos['nombre_usuario']).exists():
            return JsonResponse({'success': False, 'error': 'Nombre de usuario ya existe'}, status=400)

        password_hash = make_password(datos['password'])

        usuario = Usuario(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            fecha_nacimiento=datos['fecha_nacimiento'],
            edad=edad,
            email=datos['email'],
            telefono=datos['telefono'],
            pais=datos['pais'],
            nombre_usuario=datos['nombre_usuario'],
            password=password_hash,
            rol='cliente'  # Asignar rol por defecto como 'cliente'
        )
        usuario.save()
        return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente'})

# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    request.session.flush()
    return redirect('login')
