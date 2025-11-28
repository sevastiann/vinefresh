from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import secrets
from django.utils import timezone
from django.utils.crypto import get_random_string
from .models import Usuario, InvitacionAdmin

import logging

logger = logging.getLogger(__name__)


# -------------------------
# TOKENS TEMPORALES
# -------------------------
tokens_recuperacion = {}

# -------------------------
# UTILIDADES
# -------------------------
def usuario_logueado(request):
    """Verifica si hay un usuario logueado en la sesión"""
    return 'usuario_id' in request.session

def es_admin(request):
    """Verifica si el usuario logueado es administrador"""
    return request.session.get('usuario_rol') == 'admin'

# -------------------------
# HOME UNIFICADO
# -------------------------
def home_view(request):
    if not usuario_logueado(request):
        return redirect('login')

    rol = request.session.get('usuario_rol', 'usuario')
    contexto = {
        'nombre': request.session.get('usuario_nombre', 'Usuario'),
        'rol': rol,
    }

    # Admin ve lista de usuarios
    if rol == 'admin':
        contexto['usuarios'] = Usuario.objects.all().values(
            'id', 'nombre', 'apellido', 'email', 'rol', 'solicitud_eliminacion'
        ).order_by('-rol', 'apellido')

    return render(request, 'core/home.html', contexto)

# -------------------------
# LOGIN
# -------------------------
def login_view(request):
    mensaje = ''
    if request.method == 'POST':
        usuario_input = request.POST.get('usuario')
        clave = request.POST.get('password')

        if not usuario_input or not clave:
            mensaje = 'Por favor completa todos los campos.'
        else:
            user = Usuario.objects.filter(email__iexact=usuario_input).first() or \
                   Usuario.objects.filter(nombre_usuario__iexact=usuario_input).first()

            if user:
                # 🔥 1. Verificar si está desactivado ANTES de validar la contraseña
                if not user.estado:
                    mensaje = '⚠️ Tu cuenta ha sido desactivada. Contacta al administrador.'
                    return render(request, 'usuarios/login.html', {'mensaje': mensaje})

                # 🔥 2. Validar contraseña
                if check_password(clave, user.password):
                    request.session['usuario_id'] = user.id
                    request.session['usuario_nombre'] = user.nombre_usuario
                    request.session['usuario_rol'] = user.rol
                    return redirect('core:home')
                else:
                    mensaje = 'Usuario o contraseña incorrectos.'
            else:
                mensaje = 'Usuario o contraseña incorrectos.'

    return render(request, 'usuarios/login.html', {'mensaje': mensaje})


# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    request.session.flush()
    return redirect('usuarios:login')

# -------------------------
# REGISTRO CLIENTE
# -------------------------
def registro_view(request):
    if request.method == 'GET':
        return render(request, 'usuarios/registro.html')
    
    datos = request.POST
    campos = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento', 'email', 'telefono', 'pais', 'nombre_usuario', 'password']
    for campo in campos:
        if not datos.get(campo):
            return JsonResponse({'success': False, 'error': f'Campo {campo} requerido'}, status=400)

    # Validaciones de unicidad
    if Usuario.objects.filter(email__iexact=datos['email']).exists():
        return JsonResponse({'success': False, 'error': 'Email ya registrado'}, status=400)
    if Usuario.objects.filter(nombre_usuario__iexact=datos['nombre_usuario']).exists():
        return JsonResponse({'success': False, 'error': 'Nombre de usuario ya existe'}, status=400)
    if Usuario.objects.filter(cedula=datos['cedula']).exists():
        return JsonResponse({'success': False, 'error': 'Cédula ya registrada'}, status=400)

    # Crear usuario
    try:
        usuario = Usuario(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            cedula=datos['cedula'],
            fecha_nacimiento=datos['fecha_nacimiento'],
            email=datos['email'],
            telefono=datos['telefono'],
            pais=datos['pais'],
            nombre_usuario=datos['nombre_usuario'],
            password=make_password(datos['password']),
            rol='cliente'
        )
        usuario.save()
        return JsonResponse({'success': True, 'message': 'Usuario registrado correctamente'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al guardar: {str(e)}'}, status=500)

# -------------------------
# OLVIDAR CONTRASEÑA
# -------------------------

def olvidar_contrasena_view(request):
    mensaje = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            mensaje = 'Por favor ingresa tu correo electrónico.'
        else:
            usuario = Usuario.objects.filter(email__iexact=email).first()
            if usuario:
                token = secrets.token_urlsafe(20)
                tokens_recuperacion[token] = usuario.id

                # URL corregida con namespace
                enlace = request.build_absolute_uri(
                    reverse('usuarios:restablecer_contrasena', args=[token])
                )

                asunto = 'Recuperación de contraseña - VineFresh'
                mensaje_correo = (
                    f'Hola {usuario.nombre_usuario},\n\n'
                    f'Has solicitado restablecer tu contraseña.\n'
                    f'Haz clic en el siguiente enlace:\n{enlace}\n\n'
                    f'Si no solicitaste este cambio, ignora este mensaje.\n\n'
                    f'Equipo VineFresh 🍇'
                )
                try:
                    send_mail(asunto, mensaje_correo, settings.DEFAULT_FROM_EMAIL, [usuario.email])
                    mensaje = '✅ Se ha enviado un enlace de recuperación a tu correo.'
                except Exception:
                    mensaje = '⚠️ Error al enviar el correo. Revisa la configuración del servidor de correo.'
            else:
                mensaje = '❌ No existe ninguna cuenta asociada a ese correo.'

    return render(request, 'usuarios/olvidar_contrasena.html', {'mensaje': mensaje})


# -------------------------
# RESTABLECER CONTRASEÑA
# -------------------------
def restablecer_contrasena_view(request, token):
    mensaje = ''
    usuario_id = tokens_recuperacion.get(token)
    if not usuario_id:
        mensaje = 'El enlace de recuperación no es válido o ha expirado.'
        return render(request, 'usuarios/restablecer_contrasena.html', {'mensaje': mensaje})

    if request.method == 'POST':
        nueva_clave = request.POST.get('password')
        confirmar = request.POST.get('confirmar_password')

        if not nueva_clave or not confirmar:
            mensaje = 'Por favor completa ambos campos.'
        elif nueva_clave != confirmar:
            mensaje = 'Las contraseñas no coinciden.'
        elif len(nueva_clave) < 6:
            mensaje = 'La contraseña debe tener al menos 6 caracteres.'
        else:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.password = make_password(nueva_clave)
            usuario.save()
            del tokens_recuperacion[token]
            messages.success(request, 'Contraseña restablecida correctamente. Ahora puedes iniciar sesión.')
            return redirect('usuarios:login')  # <--- CORREGIDO

    return render(request, 'usuarios/restablecer_contrasena.html', {'mensaje': mensaje, 'token': token})

# -------------------------
# INVITACIÓN ADMINISTRADOR
# -------------------------
def enviar_invitacion_admin(request):
    if not usuario_logueado(request) or not es_admin(request):
        return redirect('home')

    if request.method == "POST":
        email_destino = request.POST.get("email")
        if not email_destino:
            return JsonResponse({"error": "Debes ingresar un correo."}, status=400)
        if Usuario.objects.filter(email__iexact=email_destino).exists() or \
           InvitacionAdmin.objects.filter(email__iexact=email_destino).exists():
            return JsonResponse({"error": "Ya existe un usuario o una invitación pendiente para este correo."}, status=400)
        try:
            token = get_random_string(50)
            InvitacionAdmin.objects.create(email=email_destino, token=token)
            enlace = request.build_absolute_uri(reverse("registro_admin", args=[token]))
            asunto = "Invitación para ser administrador en VineFresh 🍃"
            mensaje = (
                f"Hola 👋\n\nHas sido invitado a formar parte del equipo administrativo de VineFresh.\n"
                f"Completa tu registro como administrador aquí:\n\n{enlace}\n\n"
                f"Este enlace es único y expirará una vez sea usado."
            )
            send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [email_destino])
            return render(request, "usuarios/invitacion_exito.html", {"email": email_destino})
        except Exception as e:
            return JsonResponse({"error": f"Error al enviar la invitación: {str(e)}"}, status=500)

    return render(request, "usuarios/enviar_invitacion.html")

def registro_admin_view(request, token):
    invitacion = InvitacionAdmin.objects.filter(token=token).first()
    if not invitacion:
        return render(request, 'usuarios/registro.html', {'mensaje': 'El enlace no es válido o ya fue usado.'})
    email = invitacion.email
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre_usuario')
        cedula = request.POST.get('cedula')
        if Usuario.objects.filter(nombre_usuario__iexact=nombre_usuario).exists():
            return render(request, 'usuarios/registro_admin.html', {'email': email, 'mensaje': 'Nombre de usuario ya existe.'})
        if Usuario.objects.filter(cedula=cedula).exists():
            return render(request, 'usuarios/registro_admin.html', {'email': email, 'mensaje': 'Cédula ya registrada.'})
        nuevo_admin = Usuario(
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            nombre_usuario=nombre_usuario,
            password=make_password(request.POST.get('password')),
            email=email,
            cedula=cedula,
            rol='admin'
        )
        nuevo_admin.save()
        invitacion.delete()
        return redirect('login')

    return render(request, 'usuarios/registro_admin.html', {'email': email})

# -------------------------
# DETALLE DE CLIENTE
# -------------------------
def detalle_cliente(request, id):
    # opcional: control de permisos
    if not usuario_logueado(request) or not es_admin(request):
        return redirect('core:home')

    cliente = get_object_or_404(Usuario, id=id)
    return render(request, 'usuarios/detalle_cliente.html', {'cliente': cliente})

# -------------------------
# CONSULTA Y GESTIÓN DE USUARIOS (solo admin)
# -------------------------

# -------------------------
# LISTADO GENERAL DE USUARIOS
# -------------------------
def gestion_usuarios(request):
    if not usuario_logueado(request) or not es_admin(request):
        return redirect('core:home')

    usuarios = Usuario.objects.all().order_by('apellido')
    return render(request, 'usuarios/gestion_usuarios.html', {'usuarios': usuarios})


# -------------------------
# CAMBIAR ESTADO / ACTIVAR / DESACTIVAR
# -------------------------
def cambiar_estado(request, usuario_id):
    if not usuario_logueado(request) or not es_admin(request):
        return redirect('core:home')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Cambiar el estado (activo/inactivo)
    if usuario.estado:
        usuario.estado = False
        messages.warning(request, f'⚠️ Usuario {usuario.nombre_usuario} desactivado correctamente.')
    else:
        usuario.estado = True
        messages.success(request, f'✅ Usuario {usuario.nombre_usuario} activado correctamente.')

    usuario.save()
    return redirect('usuarios:detalle_cliente', id=usuario.id)

# -------------------------
# ENVIAR INVITACIÓN
# -------------------------
def enviar_invitacion_view(request):
    # Solo admin puede enviar invitaciones
    if not request.session.get('usuario_id') or request.session.get('usuario_rol') != 'admin':
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('core:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        # Validación básica
        if not email:
            messages.error(request, "Debes proporcionar un correo electrónico.")
            return render(request, 'usuarios/enviar_invitacion.html')

        # Evitar duplicados
        if Usuario.objects.filter(email=email).exists() or InvitacionAdmin.objects.filter(email=email).exists():
            messages.warning(request, "Ya existe un usuario o invitación para este correo.")
            return render(request, 'usuarios/enviar_invitacion.html', {'mensaje': 'Ya existe una invitación para ese correo.'})

        # Generar token único
        token = get_random_string(48)
        invitacion = InvitacionAdmin.objects.create(email=email, token=token, fecha_creacion=timezone.now())

        # Generar enlace correcto usando reverse
        accept_url = request.build_absolute_uri(reverse('usuarios:registro_admin_invitado', args=[token]))

        # Preparar email
        subject = "Invitación para ser administrador - VineFresh"
        message = (
            f"Hola 👋\n\n"
            f"Has sido invitado a formar parte del equipo administrativo de VineFresh.\n\n"
            f"Para aceptar la invitación y completar tu registro, haz clic en el siguiente enlace:\n{accept_url}\n\n"
            f"Este enlace es único y expirará después de usarlo.\n\n"
            f"Saludos,\nEquipo VineFresh"
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            messages.success(request, f"Invitación enviada correctamente a {email}.")
            email_enviado = True
        except BadHeaderError:
            logger.exception("BadHeaderError al enviar invitación")
            messages.error(request, "Encabezado de correo inválido. No se envió la invitación.")
            email_enviado = False
        except Exception as e:
            logger.exception("Error al enviar correo de invitación")
            messages.warning(request, f"No se pudo enviar el correo (revisa la configuración de email). La invitación quedó registrada.")
            email_enviado = False

        # Renderizar plantilla de éxito
        return render(request, 'usuarios/invitacion_exito.html', {
            'email': email,
            'email_enviado': email_enviado,
            'accept_url': accept_url,  # opcional para debug
        })

    # GET -> mostrar formulario
    return render(request, 'usuarios/enviar_invitacion.html')


# ✅ Vista para registrar administrador invitado
def registro_admin_invitado_view(request, token):
    from django.utils import timezone
    from django.contrib import messages
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.hashers import make_password
    from .models import Usuario, InvitacionAdmin

    invitacion = get_object_or_404(InvitacionAdmin, token=token)

    # 🧩 Verificar si ya fue usada
    if getattr(invitacion, 'aceptada', False):
        messages.warning(request, "Esta invitación ya fue utilizada.")
        return redirect('usuarios:login')

    if request.method == 'POST':
        print("📩 Datos recibidos:", request.POST)

        # 🧠 Capturar los datos
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        nombre_usuario = request.POST.get('nombre_usuario')
        email = request.POST.get('email')
        cedula = request.POST.get('cedula')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        telefono = request.POST.get('telefono')
        pais = request.POST.get('pais')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # 🧩 Validaciones básicas
        if not all([nombre, apellido, nombre_usuario, email, password1, password2]):
            messages.error(request, "Por favor completa todos los campos obligatorios.")
            return render(request, 'usuarios/registro_admin_invitado.html', {'token': token})

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'usuarios/registro_admin_invitado.html', {'token': token})

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Ya existe un usuario con este correo electrónico.")
            return render(request, 'usuarios/registro_admin_invitado.html', {'token': token})

        # 🧠 Crear el nuevo administrador
        nuevo_usuario = Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            nombre_usuario=nombre_usuario,
            email=email,
            cedula=cedula,
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            pais=pais,
            password=make_password(password1),
            rol='admin',
            estado=True
        )

        print("✅ Usuario creado con ID:", nuevo_usuario.id)

        # 🕒 Marcar la invitación como usada
        if hasattr(invitacion, 'aceptada'):
            invitacion.aceptada = True
            invitacion.fecha_uso = timezone.now()
            invitacion.save()
        else:
            invitacion.delete()

        # 🎉 Mensaje de éxito y redirección
        messages.success(request, "✅ Registro de administrador completado. Ya puedes iniciar sesión.")
        return redirect('usuarios:registro_exitoso')

    # GET → Mostrar formulario
    return render(request, 'usuarios/registro_admin_invitado.html', {'token': token})


# ✅ Vista de confirmación de registro exitoso
def registro_exitoso_view(request):
    return render(request, 'usuarios/registro_exitoso.html')

def configuracion_perfil(request):
    
    # -------------------------
    # 1️⃣ OBTENER USUARIO LOGUEADO DESDE LA SESIÓN
    # -------------------------
    user_id = request.session.get("usuario_id")
    if not user_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=user_id)


    # 🔥 LIMPIAR mensajes pendientes que vienen de otras vistas
    for _ in messages.get_messages(request):
        pass
    
    # -------------------------
    # 2️⃣ SI VIENE UN POST → EDITAR PERFIL
    # -------------------------
    if request.method == "POST":

        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        username = request.POST.get("username")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")

        nueva_pass = request.POST.get("nueva_contrasena")
        confirm_pass = request.POST.get("confirmar_contrasena")

        # --- Validaciones ---
        if Usuario.objects.filter(nombre_usuario=username).exclude(id=usuario.id).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect("usuarios:configuracion_perfil")

        if Usuario.objects.filter(email=email).exclude(id=usuario.id).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect("usuarios:configuracion_perfil")

        if nueva_pass and nueva_pass != confirm_pass:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("usuarios:configuracion_perfil")

        # -------------------------
        # 3️⃣ GUARDAR CAMBIOS
        # -------------------------
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.nombre_usuario = username
        usuario.telefono = telefono
        usuario.email = email

        # Cambiar contraseña solo si escribe nueva
        if nueva_pass:
            usuario.password = make_password(nueva_pass)

        usuario.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("usuarios:configuracion_perfil")

    # -------------------------
    # 4️⃣ MOSTRAR PÁGINA
    # -------------------------
    return render(request, "usuarios/configuracion_perfil.html", {
        "usuario": usuario
    })