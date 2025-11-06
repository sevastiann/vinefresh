from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from .models import Usuario
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import re
import secrets

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
        usuario_input = request.POST.get('usuario')
        clave = request.POST.get('password')

        if not usuario_input or not clave:
            mensaje = 'Por favor completa todos los campos.'
        else:
            user = Usuario.objects.filter(email=usuario_input).first() or \
                   Usuario.objects.filter(nombre_usuario=usuario_input).first()

            if user and check_password(clave, user.password):
                request.session['usuario_id'] = user.id
                request.session['usuario_nombre'] = user.nombre_usuario
                return redirect('home')
            else:
                mensaje = 'Usuario o contraseña incorrectos.'

    return render(request, 'usuarios/login.html', {'mensaje': mensaje})


# -------------------------
# OLVIDAR CONTRASEÑA
# -------------------------
tokens_recuperacion = {}  # Diccionario temporal para almacenar tokens


def olvidar_contrasena_view(request):
    """
    Vista para manejar el formulario de recuperación de contraseña,
    enviando un correo real con un enlace de recuperación.
    """
    mensaje = ''

    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            mensaje = 'Por favor ingresa tu correo electrónico.'
        else:
            usuario = Usuario.objects.filter(email=email).first()

            if usuario:
                # Generar token único
                token = secrets.token_urlsafe(20)
                tokens_recuperacion[token] = usuario.id

                # Crear enlace de recuperación completo
                enlace = request.build_absolute_uri(f'/usuarios/restablecer/{token}/')

                asunto = 'Recuperación de contraseña - VineFresh'
                mensaje_correo = (
                    f'Hola {usuario.nombre_usuario},\n\n'
                    f'Has solicitado restablecer tu contraseña.\n'
                    f'Por favor haz clic en el siguiente enlace para cambiarla:\n\n'
                    f'{enlace}\n\n'
                    f'Si no solicitaste este cambio, ignora este mensaje.\n\n'
                    f'Atentamente,\nEl equipo de VineFresh 🍇'
                )

                try:
                    send_mail(
                        asunto,
                        mensaje_correo,
                        settings.DEFAULT_FROM_EMAIL,
                        [usuario.email],
                        fail_silently=False,
                    )
                    mensaje = '✅ Se ha enviado un enlace de recuperación a tu correo.'
                except Exception as e:
                    mensaje = f'⚠️ Error al enviar el correo: {str(e)}'
            else:
                mensaje = '❌ No existe ninguna cuenta asociada a ese correo.'

    return render(request, 'usuarios/olvidar_contrasena.html', {'mensaje': mensaje})


# -------------------------
# RESTABLECER CONTRASEÑA
# -------------------------
def restablecer_contrasena_view(request, token):
    """
    Permite al usuario establecer una nueva contraseña usando el token.
    """
    mensaje = ''
    usuario_id = tokens_recuperacion.get(token)

    if not usuario_id:
        mensaje = 'El enlace de recuperación no es válido o ha expirado.'
        return render(request, 'usuarios/restablecer_contrasena.html', {'mensaje': mensaje})

    if request.method == 'POST':
        nueva_clave = request.POST.get('password')
        confirmar_clave = request.POST.get('confirmar_password')

        if not nueva_clave or not confirmar_clave:
            mensaje = 'Por favor completa ambos campos.'
        elif nueva_clave != confirmar_clave:
            mensaje = 'Las contraseñas no coinciden.'
        else:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.password = make_password(nueva_clave)
            usuario.save()

            # Eliminar el token usado
            del tokens_recuperacion[token]

            mensaje = '✅ Tu contraseña ha sido restablecida correctamente.'
            return redirect('login')

    return render(request, 'usuarios/restablecer_contrasena.html', {'mensaje': mensaje})


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
    except Exception:
        return None


def registro_view(request):
    if request.method == 'GET':
        return render(request, 'usuarios/registro.html')

    if request.method == 'POST':
        datos = request.POST
        campos = ['nombre', 'apellido', 'fecha_nacimiento', 'email', 'telefono', 'pais', 'nombre_usuario', 'password']

        # Validar campos vacíos
        for campo in campos:
            if not datos.get(campo):
                return JsonResponse({'success': False, 'error': f'Campo {campo} requerido'}, status=400)

        # Validar email
        email_ok, msg_email = validar_email(datos['email'])
        if not email_ok:
            return JsonResponse({'success': False, 'error': msg_email}, status=400)

        # Calcular edad
        edad = calcular_edad(datos['fecha_nacimiento'])
        if edad is None or edad < 18:
            return JsonResponse({'success': False, 'error': 'Debes ser mayor de 18 años'}, status=400)

        # Validar duplicados
        if Usuario.objects.filter(email=datos['email']).exists():
            return JsonResponse({'success': False, 'error': 'Email ya registrado'}, status=400)
        if Usuario.objects.filter(nombre_usuario=datos['nombre_usuario']).exists():
            return JsonResponse({'success': False, 'error': 'Nombre de usuario ya existe'}, status=400)

        # Crear usuario
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
            password=password_hash
        )
        usuario.save()

        return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente'})


# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    request.session.flush()
    return redirect('login')
