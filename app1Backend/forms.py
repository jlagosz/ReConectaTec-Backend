from django import forms
from django.core.exceptions import ValidationError
from .models import Institucion, Usuario, Donacion, Equipo, Asignacion, DetalleAsignacion, Reacondicionamiento, Soporte
import re # Para validación de RUT
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# --- Definición de Opciones (Choices) para los campos ENUM ---
# Nota: La tupla se define con (valor_en_DB, valor_en_etiqueta_HTML)

TIPO_INSTITUCION_CHOICES = [
    ('', '---------'),
    ('Donante', 'Donante'),
    ('Receptora', 'Receptora'),
    ('Ambas', 'Ambas'),
]

ROL_USUARIO_CHOICES = [
    ('', '---------'),
    ('Administrador', 'Administrador'),
    ('Tecnico', 'Técnico'),
    ('Voluntario', 'Voluntario'),
]

ESTADO_DONACION_CHOICES = [
    ('', '---------'),
    ('Pendiente', 'Pendiente'),
    ('Recibida', 'Recibida'),
    ('Cancelada', 'Cancelada'),
]

TIPO_EQUIPO_CHOICES = [
    ('', '---------'),
    ('Laptop', 'Laptop'),
    ('Desktop', 'Desktop'),
    ('Monitor', 'Monitor'),
    ('Otro', 'Otro'),
]

ESTADO_ASIGNACION_CHOICES = [
    ('', '---------'),
    ('Pendiente', 'Pendiente'),
    ('Match', 'Match'),
    ('Entregada', 'Entregada'),
    ('Rechazada', 'Rechazada'),
]

ESTADO_FINAL_CHOICES = [
    ('', '---------'),
    ('En Proceso', 'En Proceso'),
    ('Reacondicionado', 'Reacondicionado'),
    ('Irreparable', 'Irreparable'),
]

TIPO_SOPORTE_CHOICES = [
    ('', '---------'),
    ('Tecnico', 'Técnico'),
    ('Funcional', 'Funcional'),
    ('Logistico', 'Logístico'),
]

# =========================================================
# FORMS PARA CADA MODELO
# =========================================================

class InstitucionForm(forms.ModelForm):
    # Uso de forms.ChoiceField para aplicar las opciones definidas
    tipo = forms.ChoiceField(choices=TIPO_INSTITUCION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Tipo de Institución")
    
    class Meta:
        model = Institucion
        fields = ['rut', 'nombre', 'tipo', 'contacto_nombre', 'contacto_email', 'telefono', 'direccion', 'comuna']
        widgets = {
            # Los campos CharField se usan con TextInput
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 76.123.456-7'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Liceo Bicentenario'}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'contacto_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@institucion.cl'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Siempre Viva 742'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Santiago'}),
        }
        labels = {
            'rut': 'RUT/Identificador',
            'nombre': 'Nombre de la Institución',
            'contacto_nombre': 'Nombre de Contacto',
            'contacto_email': 'Email de Contacto',
        }

    def clean_rut(self):
        """Valida el formato del RUT Chileno, limpiando puntos y guiones."""
        rut = self.cleaned_data.get('rut', '').upper().replace('.', '').replace('-', '')
        
        # Formato básico: XX.XXX.XXX-X o XXXXXXXXXX
        if not re.match(r'^\d{1,9}[K0-9]$', rut):
            raise ValidationError('El RUT debe tener un formato válido (ej: 76.123.456-7).')
        
        # Vuelve a poner el formato estandarizado (sin puntos, con guion)
        self.cleaned_data['rut'] = f"{rut[:-1]}-{rut[-1]}"
        return self.cleaned_data['rut']



class CustomUserCreationForm(UserCreationForm):#cambioo
    """
    Formulario para CREAR usuarios (Usado en UsuarioCreateView)
    Maneja el hashing de la contraseña automáticamente.
    """
    rol = forms.ChoiceField(choices=ROL_USUARIO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Rol en el Sistema")

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Campos que se pedirán al CREAR
        fields = ('email', 'nombre', 'apellido', 'rol') 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilos de Bootstrap
        for field_name, field in self.fields.items():
            if field_name == 'rol':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):#cambioo
    """
    Formulario para MODIFICAR usuarios (Usado en UsuarioUpdateView)
    Maneja la contraseña de forma segura (no la muestra)
    """
    rol = forms.ChoiceField(choices=ROL_USUARIO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Rol en el Sistema")

    # Ocultamos la contraseña en el formulario de modificación
    password = None 

    class Meta(UserChangeForm.Meta):
        model = Usuario
        # Campos que se podrán EDITAR
        fields = ('email', 'nombre', 'apellido', 'rol', 'is_active') # <-- Añadimos 'is_active'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilos de Bootstrap
        for field_name, field in self.fields.items():
            if field_name == 'rol' or field_name == 'is_active':
                field.widget.attrs.update({'class': 'form-select' if field_name == 'rol' else 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class DonacionForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=ESTADO_DONACION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Estado")

    class Meta:
        model = Donacion
        fields = ['rut_institucion', 'estado', 'total_equipos']
        widgets = {
            # ForeignKey a Institucion se usa con forms.Select
            'rut_institucion': forms.Select(attrs={'class': 'form-select'}),
            'total_equipos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Cantidad de equipos'}),
        }
        labels = {
            'rut_institucion': 'Institución Donante',
        }


class EquipoForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=TIPO_EQUIPO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Tipo de Equipo")

    class Meta:
        model = Equipo
        fields = ['id_donacion', 'num_serie', 'tipo', 'marca', 'modelo', 'ram', 'almacenamiento', 'estado_inicial']
        widgets = {
            'id_donacion': forms.Select(attrs={'class': 'form-select'}),
            'num_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'S/N (Opcional)'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dell'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Latitude E7470'}),
            'ram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 8GB DDR4'}),
            'almacenamiento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 256GB SSD'}),
            'estado_inicial': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalle fallas, problemas, estado cosmético, etc.'}),
        }
        labels = {
            'id_donacion': 'Asociado a Donación',
            'num_serie': 'Número de Serie',
        }


class AsignacionForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=ESTADO_ASIGNACION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Estado")

    class Meta:
        model = Asignacion
        fields = ['rut_institucion_receptora', 'cantidad_solicitada', 'estado']
        widgets = {
            'rut_institucion_receptora': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_solicitada': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Cantidad de equipos'}),
        }
        labels = {
            'rut_institucion_receptora': 'Institución Receptora',
        }

class DetalleAsignacionForm(forms.ModelForm):
    class Meta:
        model = DetalleAsignacion
        fields = ['id_asignacion', 'id_equipo', 'fecha_entrega', 'observaciones']
        widgets = {
            'id_asignacion': forms.Select(attrs={'class': 'form-select'}),
            'id_equipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles de la entrega, persona que recibe, etc.'}),
        }
        labels = {
            'id_asignacion': 'Asignación Relacionada',
            'id_equipo': 'Equipo Entregado',
        }


class ReacondicionamientoForm(forms.ModelForm):
    estado_final = forms.ChoiceField(choices=ESTADO_FINAL_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Estado Final")

    class Meta:
        model = Reacondicionamiento
        fields = ['id_equipo', 'id_tecnico', 'taller_asignado', 'fecha_inicio', 'fecha_fin', 'acciones_realizadas', 'estado_final']
        widgets = {
            # OneToOneField id_equipo es la PK, pero se usa como FK para seleccionar el equipo
            'id_equipo': forms.Select(attrs={'class': 'form-select'}),
            'id_tecnico': forms.Select(attrs={'class': 'form-select'}),
            'taller_asignado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Taller Central'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acciones_realizadas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalle de las reparaciones: cambio de disco, aumento de RAM, etc.'}),
        }
        labels = {
            'id_equipo': 'Equipo a Reacondicionar',
            'id_tecnico': 'Técnico Asignado',
        }


class SoporteForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=TIPO_SOPORTE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Tipo de Soporte")

    class Meta:
        model = Soporte
        fields = ['id_asignacion', 'id_tecnico', 'tipo', 'descripcion', 'resolucion']
        widgets = {
            'id_asignacion': forms.Select(attrs={'class': 'form-select'}),
            'id_tecnico': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del problema o la solicitud de soporte.'}),
            'resolucion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalle de las acciones tomadas para resolver el problema (Opcional).'}),
        }
        labels = {
            'id_asignacion': 'Asignación Relacionada',
            'id_tecnico': 'Técnico Asignado',
        }