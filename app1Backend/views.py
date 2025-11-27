from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import IntegrityError
from django.utils.html import format_html, mark_safe
from django.db.models import Q # Importante para búsquedas OR (Nombre O ID)
from django.contrib.auth import update_session_auth_hash

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
    InstitucionForm,
    DonacionForm, EquipoForm, 
    AsignacionForm, ReacondicionamientoForm, SoporteForm,
    CustomUserCreationForm, CustomUserChangeForm, PerfilUsuarioForm, SoporteSolicitudForm
)

# =========================================================
# FUNCIONES DE CHEQUEO DE PERMISOS BASADAS EN ROL
# =========================================================

def is_admin(user):
    """Verifica si el usuario es Administrador."""
    return user.is_authenticated and hasattr(user, 'rol') and user.rol == 'Administrador'

def is_admin_or_tecnico(user):
    """Verifica si el usuario es Administrador o Técnico."""
    return user.is_authenticated and hasattr(user, 'rol') and user.rol in ['Administrador', 'Tecnico']

def is_admin_or_voluntario(user):
    """Verifica si el usuario es Administrador o Voluntario."""
    return user.is_authenticated and hasattr(user, 'rol') and user.rol in ['Administrador', 'Voluntario']

# La URL de inicio de sesión por defecto de Django
LOGIN_URL = '/login/' 

# =========================================================
# VISTAS BASE CON MENSAJES DE ÉXITO
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
# VISTAS PRINCIPALES (Manejo de Login y Redirección)
# =========================================================

@login_required(login_url=LOGIN_URL)
def dashboard_redirect(request):
    """
    Controla la redirección del usuario inmediatamente después del login exitoso.
    """
    try:
        rol = request.user.rol
    except AttributeError:
        messages.warning(request, "Su cuenta no tiene un rol asignado. Redirigiendo a Dashboard principal.")
        return redirect('dashboard') 

    if rol == 'Administrador':
        return redirect('dashboard')
    elif rol == 'Tecnico':
        return redirect('reacondicionamiento-list')
    elif rol == 'Voluntario':
        return redirect('donacion-list')
    
    messages.warning(request, "Rol de usuario desconocido. Redirigiendo a Dashboard principal.")
    return redirect('dashboard')


@user_passes_test(is_admin, login_url=LOGIN_URL)
def dashboard(request):
    context = {
        'total_instituciones': Institucion.objects.count(),
        'total_usuarios': Usuario.objects.count(),
        'total_donaciones': Donacion.objects.count(),
        'total_equipos': Equipo.objects.count(),
        'total_asignaciones': Asignacion.objects.count(),
        'total_reacondicionamientos': Reacondicionamiento.objects.count(),
        'total_soportes': Soporte.objects.count(),
    }
    return render(request, 'app1Backend/dashboard.html', context)


# =========================================================
# VISTAS CRUD CON BÚSQUEDA ACTUALIZADA (ID Y NOMBRE)
# =========================================================

# --- CRUD para Instituciones ---

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class InstitucionListView(ListView):
    model = Institucion
    template_name = 'app1Backend/institucion_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por Nombre O RUT (que es el ID en este caso)
            return Institucion.objects.filter(
                Q(nombre__icontains=query) | 
                Q(rut__icontains=query)
            )
        return Institucion.objects.all()

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
            asignaciones_asociadas = self.object.asignacion_set.all() 
            error_message = f"No se puede eliminar la institución '{self.object.nombre}' porque tiene registros asociados."
            messages.error(request, error_message)
            return redirect(self.success_url)


# --- CRUD para Usuarios ---

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class UsuarioListView(ListView):
    model = Usuario
    template_name = 'app1Backend/usuario_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por ID, Nombre, Apellido o Email
            return Usuario.objects.filter(
                Q(id_usuario__icontains=query) | # Busca por ID numérico
                Q(nombre__icontains=query) | 
                Q(apellido__icontains=query) |
                Q(email__icontains=query)
            )
        return Usuario.objects.all()

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
            messages.error(request, f"No se puede eliminar al usuario '{self.object}' porque tiene tareas activas.")
            return redirect(self.success_url)

# --- VISTA DE PERFIL DE USUARIO (Cualquier rol) ---
@method_decorator(login_required(login_url=LOGIN_URL), name='dispatch')
class PerfilUsuarioUpdateView(SuccessMessageUpdateView):
    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = 'app1Backend/usuario_perfil.html'
    success_url = reverse_lazy('dashboard-redirect')
    success_message = "¡Tu perfil ha sido actualizado exitosamente!"

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Guardamos el usuario con los datos nuevos
        response = super().form_valid(form)
        
        # Si el usuario cambió su contraseña, actualizamos la sesión para que no se desconecte
        if form.cleaned_data.get('new_password'):
            update_session_auth_hash(self.request, self.object)
            
        return response

# --- CRUD para Donaciones ---

@method_decorator(user_passes_test(is_admin_or_voluntario, login_url=LOGIN_URL), name='dispatch')
class DonacionListView(ListView):
    model = Donacion
    template_name = 'app1Backend/donacion_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por ID de Donación O Nombre de la Institución
            return Donacion.objects.filter(
                Q(id_donacion__icontains=query) | # Busca por ID numérico
                Q(rut_institucion__nombre__icontains=query) | 
                Q(rut_institucion__rut__icontains=query)
            )
        return Donacion.objects.all()

@method_decorator(user_passes_test(is_admin_or_voluntario, login_url=LOGIN_URL), name='dispatch')
class DonacionCreateView(SuccessMessageCreateView):
    model = Donacion
    form_class = DonacionForm
    template_name = 'app1Backend/donacion_form.html'
    success_url = reverse_lazy('donacion-list')
    success_message = "¡Donación registrada exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class DonacionUpdateView(SuccessMessageUpdateView):
    model = Donacion
    form_class = DonacionForm
    template_name = 'app1Backend/donacion_form.html'
    success_url = reverse_lazy('donacion-list')
    success_message = "¡Donación modificada exitosamente!"

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
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
            messages.error(request, f"No se puede eliminar la donación porque tiene Equipos asociados.")
            return redirect(self.success_url)


# --- CRUD para Equipos ---

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class EquipoListView(ListView):
    model = Equipo
    template_name = 'app1Backend/equipo_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por ID de Equipo, Marca, Modelo o Serie
            return Equipo.objects.filter(
                Q(id_equipo__icontains=query) | # Busca por ID numérico
                Q(marca__icontains=query) | 
                Q(modelo__icontains=query) |
                Q(num_serie__icontains=query)
            )
        return Equipo.objects.all()

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
            messages.error(request, f"No se puede eliminar el equipo porque tiene registros asociados (Reacondicionamiento o Asignación).")
            return redirect(self.success_url)


# --- CRUD para Asignaciones ---

@method_decorator(user_passes_test(is_admin, login_url=LOGIN_URL), name='dispatch')
class AsignacionListView(ListView):
    model = Asignacion
    template_name = 'app1Backend/asignacion_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por ID de Asignación O Nombre de la Institución Receptora
            return Asignacion.objects.filter(
                Q(id_asignacion__icontains=query) | # Busca por ID numérico
                Q(rut_institucion_receptora__nombre__icontains=query) |
                Q(rut_institucion_receptora__rut__icontains=query)
            )
        return Asignacion.objects.all()

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
            messages.error(request, f"No se puede eliminar la asignación porque tiene detalles o soportes asociados.")
            return redirect(self.success_url)


# --- CRUD para Reacondicionamientos ---

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class ReacondicionamientoListView(ListView):
    model = Reacondicionamiento
    template_name = 'app1Backend/reacondicionamiento_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por ID del Equipo (PK) O Nombre del Técnico
            return Reacondicionamiento.objects.filter(
                Q(id_equipo__id_equipo__icontains=query) | # ID del equipo relacionado
                Q(id_equipo__num_serie__icontains=query) | # Serie del equipo
                Q(id_tecnico__nombre__icontains=query)     # Nombre del técnico
            )
        return Reacondicionamiento.objects.all()

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
            messages.error(request, f"No se puede eliminar el registro debido a una restricción de la base de datos.")
            return redirect(self.success_url)


# --- CRUD para Soportes ---

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class SoporteListView(ListView):
    model = Soporte
    template_name = 'app1Backend/soporte_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por ID de Soporte, Descripción O Nombre del Técnico
            return Soporte.objects.filter(
                Q(id_soporte__icontains=query) | # Busca por ID numérico
                Q(descripcion__icontains=query) |
                Q(id_tecnico__nombre__icontains=query) |
                Q(id_asignacion__id_asignacion__icontains=query)
            )
        return Soporte.objects.all()

@method_decorator(user_passes_test(is_admin_or_tecnico, login_url=LOGIN_URL), name='dispatch')
class SoporteCreateView(SuccessMessageCreateView):
    model = Soporte
    form_class = SoporteSolicitudForm
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