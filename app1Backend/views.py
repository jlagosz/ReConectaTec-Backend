from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import IntegrityError
from django.utils.html import format_html, mark_safe

# --- DECORADORES NECESARIOS ---
from django.utils.decorators import method_decorator
# user_passes_test es el decorador clave para chequear roles
from django.contrib.auth.decorators import login_required, user_passes_test

# Importamos TODOS los modelos y formularios que vamos a usar
from .models import (
    Institucion, Usuario, Donacion, Equipo, 
    Asignacion, Reacondicionamiento, Soporte
)
from .forms import (
    InstitucionForm, # <-- Aquí estaba UsuarioForm, lo borramos
    DonacionForm, EquipoForm, 
    AsignacionForm, ReacondicionamientoForm, SoporteForm,
    CustomUserCreationForm, CustomUserChangeForm # <-- Añadimos los 2 nuevos
)

# =========================================================
# FUNCIONES DE CHEQUEO DE PERMISOS BASADAS EN ROL
# =========================================================
# Estas funciones se usan con user_passes_test()

# Nota: La existencia de 'user.rol' asume que tu modelo Usuario
# está vinculado al User de Django o es un User personalizado.

def is_admin(user):
    """Verifica si el usuario es Administrador."""
    # Usamos user.is_authenticated para asegurar que no es un usuario anónimo
    return user.is_authenticated and hasattr(user, 'rol') and user.rol == 'Administrador'

def is_admin_or_tecnico(user):
    """Verifica si el usuario es Administrador o Técnico."""
    return user.is_authenticated and hasattr(user, 'rol') and user.rol in ['Administrador', 'Tecnico']

def is_admin_or_voluntario(user):
    """Verifica si el usuario es Administrador o Voluntario."""
    return user.is_authenticated and hasattr(user, 'rol') and user.rol in ['Administrador', 'Voluntario']

# La URL de inicio de sesión por defecto de Django se usa si el chequeo falla
LOGIN_URL = '/login/' 

# =========================================================
# VISTAS BASE CON MENSAJES DE ÉXITO (Sin cambios)
# =========================================================

class SuccessMessageCreateView(CreateView):
    success_message = "¡Registro creado exitosamente!"
    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

class SuccessMessageUpdateView(UpdateView):
    success_message = "¡Registro modificado exitosamente!"
    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


# =========================================================
# VISTAS PRINCIPALES (Manejo de Login y Redirección de Roles)
# =========================================================

# --- 1. VISTA DISPATCHER (Redirección por Rol) ---
@login_required(login_url=LOGIN_URL)
def dashboard_redirect(request):
    """
    Controla la redirección del usuario inmediatamente después del login exitoso,
    basándose en su campo 'rol' para enviarlo a su página de inicio específica.
    """
    try:
        rol = request.user.rol
    except AttributeError:
        # Si el campo 'rol' no existe (ej. Superuser de Django sin rol en el modelo extendido)
        messages.warning(request, "Su cuenta no tiene un rol asignado. Redirigiendo a Dashboard principal.")
        # Se redirige a la vista principal del Administrador, que ya tiene el chequeo.
        return redirect('dashboard') 

    if rol == 'Administrador':
        # Redirige a la vista del dashboard principal (ahora renombrada 'dashboard')
        return redirect('dashboard')
    elif rol == 'Tecnico':
        # Redirige a la lista de tareas de reacondicionamiento
        return redirect('reacondicionamiento-list')
    elif rol == 'Voluntario':
        # Redirige a la lista de donaciones para gestionar
        return redirect('donacion-list')
    
    # Si el rol es desconocido (mantiene la lógica de fallback)
    messages.warning(request, "Rol de usuario desconocido. Redirigiendo a Dashboard principal.")
    return redirect('dashboard') # Redirige al dashboard principal (Administrador)


# --- 2. VISTA DASHBOARD DE ADMINISTRADOR (Contenido) ---
@user_passes_test(is_admin, login_url=LOGIN_URL) # MANTENER ESTA RESTRICCIÓN
def dashboard(request): # Renombrada de dashboard_admin a dashboard por convención de ruta principal
    context = {
        'total_instituciones': Institucion.objects.count(),
        'total_usuarios': Usuario.objects.count(),
        'total_donaciones': Donacion.objects.count(),
        'total_equipos': Equipo.objects.count(),
        'total_asignaciones': Asignacion.objects.count(),
        'total_reacondicionamientos': Reacondicionamiento.objects.count(),
        'total_soportes': Soporte.objects.count(),
    }
    # Esta función renderiza el 'dashboard.html' con todas las métricas.
    return render(request, 'app1Backend/dashboard.html', context)


# =========================================================
# VISTAS CRUD CON RESTRICCIONES DE ROL
# =========================================================

# --- CRUD para Instituciones (SOLO ADMINISTRADOR) ---

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class InstitucionListView(ListView):
    model = Institucion
    template_name = 'app1Backend/institucion_list.html'

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class InstitucionCreateView(SuccessMessageCreateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'app1Backend/institucion_form.html'
    success_url = reverse_lazy('institucion-list')
    success_message = "¡Institución creada exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class InstitucionUpdateView(SuccessMessageUpdateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'app1Backend/institucion_form.html'
    success_url = reverse_lazy('institucion-list')
    success_message = "¡Institución modificada exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class InstitucionDeleteView(DeleteView):
    model = Institucion
    success_url = reverse_lazy('institucion-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, f"La institución '{self.object.nombre}' fue eliminada exitosamente.")
            return redirect(self.success_url)
        except IntegrityError:
            donaciones_asociadas = self.object.donacion_set.all()
            # Asume que Asignacion tiene un campo rut_institucion_receptora
            asignaciones_asociadas = self.object.asignacion_set.all() 
            
            error_message = f"No se puede eliminar la institución '{self.object.nombre}' porque tiene registros asociados. "
            
            if donaciones_asociadas:
                lista_donaciones = ", ".join([f"'{str(d)}'" for d in donaciones_asociadas])
                error_message += f"Debe eliminar primero las siguientes Donaciones: {lista_donaciones}. "
            
            if asignaciones_asociadas:
                lista_asignaciones = ", ".join([f"'{str(a)}'" for a in asignaciones_asociadas])
                error_message += f"Debe eliminar primero las siguientes Asignaciones: {lista_asignaciones}."

            messages.error(request, error_message)
            return redirect(self.success_url)


# --- CRUD para Usuarios (SOLO ADMINISTRADOR) ---

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class UsuarioListView(ListView):
    model = Usuario
    template_name = 'app1Backend/usuario_list.html'

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class UsuarioCreateView(SuccessMessageCreateView):
    model = Usuario
    form_class = CustomUserCreationForm
    template_name = 'app1Backend/usuario_form.html'
    success_url = reverse_lazy('usuario-list')
    success_message = "¡Usuario creado exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class UsuarioUpdateView(SuccessMessageUpdateView):
    model = Usuario
    form_class = CustomUserChangeForm
    template_name = 'app1Backend/usuario_form.html'
    success_url = reverse_lazy('usuario-list')
    success_message = "¡Usuario modificado exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class UsuarioDeleteView(DeleteView):
    model = Usuario
    success_url = reverse_lazy('usuario-list')
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, f"El usuario '{self.object}' fue eliminado exitosamente.")
            return redirect(self.success_url)
        except IntegrityError:
            # Aquí asumimos que las dependencias vienen de Reacondicionamiento y Soporte
            messages.error(request, f"No se puede eliminar al usuario '{self.object}' porque está asignado a tareas activas (reacondicionamientos o soporte).")
            return redirect(self.success_url)


# --- CRUD para Donaciones (ADMINISTRADOR O VOLUNTARIO) ---

@method_decorator(user_passes_test(is_admin_or_voluntario, login_url=LOGIN_URL), name='dispatch')
class DonacionListView(ListView):
    model = Donacion
    template_name = 'app1Backend/donacion_list.html'

@method_decorator(user_passes_test(is_admin_or_voluntario, login_url=LOGIN_URL), name='dispatch')
class DonacionCreateView(SuccessMessageCreateView):
    model = Donacion
    form_class = DonacionForm
    template_name = 'app1Backend/donacion_form.html'
    success_url = reverse_lazy('donacion-list')
    success_message = "¡Donación registrada exitosamente!"

@method_decorator(user_passes_test(is_admin_or_voluntario, login_url=LOGIN_URL), name='dispatch')
class DonacionUpdateView(SuccessMessageUpdateView):
    model = Donacion
    form_class = DonacionForm
    template_name = 'app1Backend/donacion_form.html'
    success_url = reverse_lazy('donacion-list')
    success_message = "¡Donación modificada exitosamente!"

@method_decorator(user_passes_test(is_admin_or_voluntario, login_url=LOGIN_URL), name='dispatch')
class DonacionDeleteView(DeleteView):
    model = Donacion
    success_url = reverse_lazy('donacion-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, f"La donación '{self.object}' fue eliminada exitosamente.")
            return redirect(self.success_url)
        except IntegrityError:
            equipos_asociados = self.object.equipo_set.all()
            lista_equipos = ", ".join([f"'{str(e)}'" for e in equipos_asociados])
            error_message = f"No se puede eliminar la donación '{self.object}' porque tiene Equipos asociados. Debe eliminar primero: {lista_equipos}."
            messages.error(request, error_message)
            return redirect(self.success_url)


# --- CRUD para Equipos (ADMINISTRADOR O TÉCNICO) ---

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class EquipoListView(ListView):
    model = Equipo
    template_name = 'app1Backend/equipo_list.html'

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class EquipoCreateView(SuccessMessageCreateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'app1Backend/equipo_form.html'
    success_url = reverse_lazy('equipo-list')
    success_message = "¡Equipo creado exitosamente!"

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class EquipoUpdateView(SuccessMessageUpdateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'app1Backend/equipo_form.html'
    success_url = reverse_lazy('equipo-list')
    success_message = "¡Equipo modificado exitosamente!"

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class EquipoDeleteView(DeleteView):
    model = Equipo
    success_url = reverse_lazy('equipo-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, f"El equipo '{self.object}' fue eliminado exitosamente.")
            return redirect(self.success_url)
        except IntegrityError:
            dependencies = []
            
            # Reacondicionamiento es una relación OneToOne (por defecto) o ForeignKey única
            if hasattr(self.object, 'reacondicionamiento'):
                try:
                    reac = self.object.reacondicionamiento
                    dependencies.append(f"el registro de reacondicionamiento '{reac}'")
                except Reacondicionamiento.DoesNotExist:
                    pass

            # Asume que DetalleAsignacion tiene un campo relacionado `equipo`
            if hasattr(self.object, 'detalleasignacion_set'):
                detalles = self.object.detalleasignacion_set.all()
                if detalles.exists():
                    lista_detalles = ", ".join([f"'{str(d)}'" for d in detalles])
                    dependencies.append(f"Detalles de Asignación: {lista_detalles}")
            
            error_message = f"No se puede eliminar el equipo '{self.object}' porque está asociado a: {', '.join(dependencies)}. Por favor, elimínelos primero."
            messages.error(request, error_message)
            return redirect(self.success_url)


# --- CRUD para Asignaciones (SOLO ADMINISTRADOR) ---

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class AsignacionListView(ListView):
    model = Asignacion
    template_name = 'app1Backend/asignacion_list.html'

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class AsignacionCreateView(SuccessMessageCreateView):
    model = Asignacion
    form_class = AsignacionForm
    template_name = 'app1Backend/asignacion_form.html'
    success_url = reverse_lazy('asignacion-list')
    success_message = "¡Asignación creada exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class AsignacionUpdateView(SuccessMessageUpdateView):
    model = Asignacion
    form_class = AsignacionForm
    template_name = 'app1Backend/asignacion_form.html'
    success_url = reverse_lazy('asignacion-list')
    success_message = "¡Asignación modificada exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class AsignacionDeleteView(DeleteView):
    model = Asignacion
    success_url = reverse_lazy('asignacion-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, f"La asignación '{self.object}' fue eliminada exitosamente.")
            return redirect(self.success_url)
        except IntegrityError:
            dependencies = []
            # Asume que DetalleAsignacion está relacionado con Asignacion
            detalles_asociados = [] # self.object.detalleasignacion_set.all() # Descomentar si existe
            soportes_asociados = self.object.soporte_set.all()

            if detalles_asociados:
                lista_detalles = ", ".join([f"'{str(d)}'" for d in detalles_asociados])
                dependencies.append(f"Detalles de Asignación: {lista_detalles}")
            if soportes_asociados:
                lista_soportes = ", ".join([f"'{str(s)}'" for s in soportes_asociados])
                dependencies.append(f"Tickets de Soporte: {lista_soportes}")

            error_message = f"No se puede eliminar la asignación '{self.object}' porque tiene los siguientes elementos asociados. Debe eliminarlos primero. ({'; '.join(dependencies)})"
            messages.error(request, error_message)
            return redirect(self.success_url)


# --- CRUD para Reacondicionamientos (ADMINISTRADOR O TÉCNICO) ---

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class ReacondicionamientoListView(ListView):
    model = Reacondicionamiento
    template_name = 'app1Backend/reacondicionamiento_list.html'

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class ReacondicionamientoCreateView(SuccessMessageCreateView):
    model = Reacondicionamiento
    form_class = ReacondicionamientoForm
    template_name = 'app1Backend/reacondicionamiento_form.html'
    success_url = reverse_lazy('reacondicionamiento-list')
    success_message = "¡Registro de reacondicionamiento creado!"

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class ReacondicionamientoUpdateView(SuccessMessageUpdateView):
    model = Reacondicionamiento
    form_class = ReacondicionamientoForm
    template_name = 'app1Backend/reacondicionamiento_form.html'
    success_url = reverse_lazy('reacondicionamiento-list')
    success_message = "¡Registro de reacondicionamiento modificado!"

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class ReacondicionamientoDeleteView(DeleteView):
    model = Reacondicionamiento
    success_url = reverse_lazy('reacondicionamiento-list')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "El registro de reacondicionamiento fue eliminado exitosamente.")
            return redirect(self.success_url)
        except IntegrityError:
            # En teoría no debería haber IntegrityError al borrar Reacondicionamiento,
            # pero se deja por buena práctica.
            messages.error(request, f"No se puede eliminar el registro para el equipo '{self.object.id_equipo}' debido a una restricción de la base de datos.")
            return redirect(self.success_url)


# --- CRUD para Soportes (ADMINISTRADOR O TÉCNICO) ---

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class SoporteListView(ListView):
    model = Soporte
    template_name = 'app1Backend/soporte_list.html'

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class SoporteCreateView(SuccessMessageCreateView):
    model = Soporte
    form_class = SoporteForm
    template_name = 'app1Backend/soporte_form.html'
    success_url = reverse_lazy('soporte-list')
    success_message = "¡Ticket de soporte creado!"

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class SoporteUpdateView(SuccessMessageUpdateView):
    model = Soporte
    form_class = SoporteForm
    template_name = 'app1Backend/soporte_form.html'
    success_url = reverse_lazy('soporte-list')
    success_message = "¡Ticket de soporte modificado!"

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class SoporteDeleteView(DeleteView):
    model = Soporte
    success_url = reverse_lazy('soporte-list')
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "El ticket de soporte fue eliminado exitosamente.")
        return redirect(self.success_url)