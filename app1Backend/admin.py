from django.contrib import admin, messages
from .models import (
    Institucion, Usuario, Donacion, Equipo,
    Asignacion, DetalleAsignacion, Reacondicionamiento, Soporte
)
from django.contrib.auth.admin import UserAdmin
# =========================================================
# Custom ModelAdmin para cada modelo
# =========================================================

@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la vista de lista
    list_display = ('rut', 'nombre', 'tipo', 'contacto_email', 'comuna', 'fecha_registro')
    # Campos por los que se puede buscar
    search_fields = ('rut', 'nombre', 'contacto_email', 'comuna')
    # Filtros laterales
    list_filter = ('tipo', 'comuna', 'fecha_registro')
    # Campo por defecto para ordenar
    ordering = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin): # <-- CAMBIA ModelAdmin por UserAdmin
    # Campos que se mostrarán en la vista de lista
    list_display = ('email', 'nombre', 'apellido', 'rol', 'is_staff', 'is_active')
    # Campos por los que se puede buscar
    search_fields = ('nombre', 'apellido', 'email')
    # Filtros laterales
    list_filter = ('rol', 'is_staff', 'is_active', 'fecha_creacion')
    # Campo por defecto para ordenar
    ordering = ('apellido', 'nombre')

    # --- Configuración necesaria para UserAdmin con modelo custom ---
    # Campos en el formulario de MODIFICACIÓN
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('fecha_creacion',)}),
    )
    # Campos en el formulario de CREACIÓN
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'nombre', 'apellido', 'rol'),
        }),
    )
    # Campos de solo lectura
    readonly_fields = ('fecha_creacion',)

    # --- SEGURIDAD: PROTECCIÓN DE SUPERUSUARIO ---

    def has_delete_permission(self, request, obj=None):
        """
        Desactiva el botón de eliminar si el usuario que se está viendo es Superusuario.
        """
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Bloquea la eliminación masiva (seleccionar varios -> eliminar)
        si en la selección hay al menos un Superusuario.
        """
        if queryset.filter(is_superuser=True).exists():
            # Si hay un superusuario en la lista seleccionada, mostramos error y no hacemos nada.
            self.message_user(request, "ACCIÓN DENEGADA: No se puede eliminar a Superusuarios desde el panel.", level=messages.ERROR)
        else:
            # Si no hay superusuarios, procedemos con el borrado normal.
            super().delete_queryset(request, queryset)

@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    # Para ForeignKeys, se usa __nombre_del_campo para mostrar algo útil
    list_display = ('id_donacion', 'rut_institucion', 'fecha_oferta', 'estado', 'total_equipos')
    search_fields = ('rut_institucion__nombre', 'rut_institucion__rut', 'id_donacion')
    list_filter = ('estado', 'fecha_oferta')
    ordering = ('-fecha_oferta',)
    # Muestra la ForeignKey como un campo de búsqueda en lugar de un select simple
    raw_id_fields = ('rut_institucion',)

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('id_equipo', 'tipo', 'marca', 'modelo', 'num_serie', 'get_institucion_donante')
    search_fields = ('num_serie', 'marca', 'modelo', 'id_donacion__rut_institucion__nombre')
    list_filter = ('tipo', 'marca', 'id_donacion__rut_institucion__nombre')
    ordering = ('tipo', 'marca')
    raw_id_fields = ('id_donacion',)

    # Método para obtener la institución donante a través de la donación
    def get_institucion_donante(self, obj):
        return obj.id_donacion.rut_institucion.nombre if obj.id_donacion and obj.id_donacion.rut_institucion else 'N/A'
    get_institucion_donante.short_description = 'Institución Donante'


# --- Inlines (para tablas de detalle) ---

class DetalleAsignacionInline(admin.TabularInline):
    """Muestra los equipos asignados directamente en la vista de Asignación."""
    model = DetalleAsignacion
    # El equipo se debe seleccionar de los equipos disponibles.
    # Como id_equipo es OneToOneField en el modelo, el inlines es eficiente.
    extra = 0  # No muestra campos vacíos por defecto
    raw_id_fields = ('id_equipo',)


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('id_asignacion', 'rut_institucion_receptora', 'fecha_solicitud', 'cantidad_solicitada', 'estado')
    search_fields = ('rut_institucion_receptora__nombre', 'rut_institucion_receptora__rut', 'id_asignacion')
    list_filter = ('estado', 'fecha_solicitud')
    ordering = ('-fecha_solicitud',)
    raw_id_fields = ('rut_institucion_receptora',)
    # Incluye el detalle de los equipos asignados
    inlines = [DetalleAsignacionInline]


# DetalleAsignacionAdmin solo si se quiere gestionar por separado, pero no es recomendable si se usa Inline
# @admin.register(DetalleAsignacion)
# class DetalleAsignacionAdmin(admin.ModelAdmin):
#     list_display = ('id_asignacion', 'id_equipo', 'fecha_entrega')
#     search_fields = ('id_asignacion__id_asignacion', 'id_equipo__num_serie')
#     raw_id_fields = ('id_asignacion', 'id_equipo')


@admin.register(Reacondicionamiento)
class ReacondicionamientoAdmin(admin.ModelAdmin):
    list_display = ('id_equipo', 'id_tecnico', 'taller_asignado', 'estado_final', 'fecha_inicio', 'fecha_fin')
    search_fields = ('id_equipo__num_serie', 'id_equipo__marca', 'id_tecnico__nombre', 'taller_asignado')
    list_filter = ('estado_final', 'taller_asignado', 'fecha_inicio', 'fecha_fin')
    ordering = ('estado_final', 'taller_asignado')
    # id_equipo y id_tecnico son ForeignKeys/OneToOneFields, se usan raw_id_fields
    raw_id_fields = ('id_equipo', 'id_tecnico')


@admin.register(Soporte)
class SoporteAdmin(admin.ModelAdmin):
    list_display = ('id_soporte', 'id_asignacion', 'tipo', 'id_tecnico', 'fecha_evento')
    search_fields = ('id_asignacion__id_asignacion', 'id_tecnico__nombre', 'descripcion')
    list_filter = ('tipo', 'fecha_evento')
    ordering = ('-fecha_evento',)
    raw_id_fields = ('id_asignacion', 'id_tecnico')