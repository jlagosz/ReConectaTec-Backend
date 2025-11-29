from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.conf import settings

# La URL a la que se redirigirá si el chequeo de permisos falla.
# Asumo que tienes una ruta de login o un manejo de 403 (Acceso Denegado).
# Si no está definida en settings, se usa un valor por defecto.
LOGIN_URL = getattr(settings, 'LOGIN_URL', '/login/')


# =========================================================
# FUNCIONES BASE PARA user_passes_test
# =========================================================

def user_is_admin(user):
    """Verifica si el usuario tiene el rol de Administrador."""
    # Asume que el modelo de usuario tiene un campo 'rol'
    # y que 'Administrador' es el valor exacto en el campo.
    return user.is_authenticated and user.rol == 'Administrador'

def user_is_tecnico(user):
    """Verifica si el usuario tiene el rol de Técnico."""
    return user.is_authenticated and user.rol == 'Tecnico'

def user_is_voluntario(user):
    """Verifica si el usuario tiene el rol de Voluntario."""
    return user.is_authenticated and user.rol == 'Voluntario'

def user_is_admin_or_tecnico(user):
    """Verifica si el usuario tiene el rol de Administrador O Técnico."""
    return user.is_authenticated and user.rol in ['Administrador', 'Tecnico']

def user_is_admin_or_voluntario(user):
    """Verifica si el usuario tiene el rol de Administrador O Voluntario."""
    return user.is_authenticated and user.rol in ['Administrador', 'Voluntario']


# =========================================================
# DECORADORES REUTILIZABLES
# =========================================================

# El decorador 'login_required' se aplica automáticamente porque
# user_passes_test() lo incluye implícitamente si el test_func retorna False
# para un usuario no autenticado (como lo hacen nuestras funciones base).

def admin_required(function=None, login_url=LOGIN_URL):
    """Restringe el acceso solo a usuarios con rol 'Administrador'."""
    actual_decorator = user_passes_test(
        user_is_admin,
        login_url=login_url,
        # redirect_field_name=None para no añadir el parámetro 'next' a la URL
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def tecnico_required(function=None, login_url=LOGIN_URL):
    """Restringe el acceso solo a usuarios con rol 'Técnico'."""
    actual_decorator = user_passes_test(
        user_is_tecnico,
        login_url=login_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def voluntario_required(function=None, login_url=LOGIN_URL):
    """Restringe el acceso solo a usuarios con rol 'Voluntario'."""
    actual_decorator = user_passes_test(
        user_is_voluntario,
        login_url=login_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_tecnico_required(function=None, login_url=LOGIN_URL):
    """Restringe el acceso solo a usuarios con rol 'Administrador' o 'Técnico'."""
    actual_decorator = user_passes_test(
        user_is_admin_or_tecnico,
        login_url=login_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_voluntario_required(function=None, login_url=LOGIN_URL):
    """Restringe el acceso solo a usuarios con rol 'Administrador' o 'Voluntario'."""
    actual_decorator = user_passes_test(
        user_is_admin_or_voluntario,
        login_url=login_url,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def is_todas_las_cuentas(user):
    """Permite el acceso a Administrador, Técnico y Voluntario."""
    return user.is_authenticated and user.rol in ['Administrador', 'Tecnico', 'Voluntario']

def is_soporte_access(user):
    """Permite entrar a Admin, Técnico y Voluntario."""
    return user.is_authenticated and user.rol in ['Administrador', 'Tecnico', 'Voluntario']