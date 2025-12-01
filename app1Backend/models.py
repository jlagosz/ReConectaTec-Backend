from django.db import models
# Necesario para el Custom User Model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.utils import timezone

# NOTA: La opción `on_delete=models.DO_NOTHING` se mantiene en las tablas Institucion->Donacion/Asignacion
# por la lógica de la base de datos existente (generada por `inspectdb`), pero se han
# realizado correcciones a `models.CASCADE` o `models.SET_NULL` en otras relaciones dependientes
# para mejorar la integridad referencial y seguir las buenas prácticas de Django.


# =========================================================
# 1. MANAGER PERSONALIZADO PARA EL MODELO USUARIO
# =========================================================

class CustomUsuarioManager(BaseUserManager):
    """Define el manager para el modelo Usuario, donde el email es el identificador único."""
    
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('El email debe ser configurado')
        # Normalizamos el email para que sea minúscula
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # set_password es la función de Django que hashea la contraseña
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Crea un superusuario con rol 'Administrador' y todos los permisos."""
        # Se asegura de que estos campos estén configurados para Superusuario
        extra_fields.setdefault('rol', 'Administrador')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


# =========================================================
# 2. MODELO USUARIO (CUSTOM USER MODEL)
# =========================================================

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(db_column='ID_Usuario', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100)
    apellido = models.CharField(db_column='Apellido', max_length=100)
    
    email = models.EmailField(db_column='Email', unique=True, max_length=100)
    rol = models.CharField(db_column='Rol', max_length=13)
    
    # Campos de seguridad obligatorios de Django
    is_staff = models.BooleanField(default=False)      # Acceso al Admin de Django
    is_active = models.BooleanField(default=True)     # Indica si la cuenta está activa
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', default=timezone.now)
    
    # 📌 FIX para SystemCheckError (E304): Se añaden related_name únicos para evitar el "clash"
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        # Usamos el nombre de la app (app1Backend) como prefijo para asegurar unicidad
        related_name="app1Backend_usuario_set", 
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        # Usamos el nombre de la app (app1Backend) como prefijo para asegurar unicidad
        related_name="app1Backend_usuario_permissions", 
        related_query_name="usuario",
    )
    # Fin del FIX

    # Configuración de Django
    USERNAME_FIELD = 'email'  # Campo usado para iniciar sesión
    REQUIRED_FIELDS = ['nombre', 'apellido', 'rol'] # Campos pedidos al crear un usuario
    objects = CustomUsuarioManager()

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"

    # Métodos requeridos por Django para compatibilidad
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre


# =========================================================
# 3. DEMÁS MODELOS (Institucion, Donacion, Equipo, etc.)
# =========================================================

class Institucion(models.Model):
    #agregar id
    rut = models.CharField(db_column='RUT', primary_key=True, max_length=12)
    nombre = models.CharField(db_column='Nombre', max_length=255)
    tipo = models.CharField(db_column='Tipo', max_length=9)
    contacto_nombre = models.CharField(db_column='Contacto_Nombre', max_length=100, blank=True, null=True)
    contacto_email = models.CharField(db_column='Contacto_Email', unique=True, max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    comuna = models.CharField(db_column='Comuna', max_length=100, blank=True, null=True)
    fecha_registro = models.DateField(db_column='Fecha_Registro', auto_now_add=True)

    class Meta:
        db_table = 'institucion'

    def __str__(self):
        return self.nombre

class Donacion(models.Model):
    id_donacion = models.AutoField(db_column='ID_Donacion', primary_key=True)
    # Mantiene DO_NOTHING por la nota de `inspectdb` / DB existente.
    rut_institucion = models.ForeignKey(Institucion, models.DO_NOTHING, db_column='RUT_Institucion')
    fecha_oferta = models.DateField(db_column='Fecha_Oferta', auto_now_add=True)
    estado = models.CharField(db_column='Estado', max_length=9)
    total_equipos = models.IntegerField(db_column='Total_Equipos')

    class Meta:
        db_table = 'donacion'

    def __str__(self):
        return f"Donación #{self.id_donacion} de {self.rut_institucion.nombre}"

class Equipo(models.Model):
    id_equipo = models.AutoField(db_column='ID_Equipo', primary_key=True)
    id_donacion = models.ForeignKey(Donacion, models.CASCADE, db_column='ID_Donacion')
    num_serie = models.CharField(db_column='Num_Serie', unique=True, max_length=50, blank=True, null=True)
    tipo = models.CharField(db_column='Tipo', max_length=7)
    marca = models.CharField(db_column='Marca', max_length=50, blank=True, null=True)
    modelo = models.CharField(db_column='Modelo', max_length=100, blank=True, null=True)
    ram = models.CharField(db_column='RAM', max_length=20, blank=True, null=True)
    almacenamiento = models.CharField(db_column='Almacenamiento', max_length=50, blank=True, null=True)
    estado_inicial = models.TextField(db_column='Estado_Inicial', blank=True, null=True)
    imagen = models.ImageField(upload_to='equipos/', blank=True, null=True, verbose_name="Foto del Equipo")

    class Meta:
        db_table = 'equipo'

    def __str__(self):
        # Usamos 'or' para evitar errores si un campo está vacío.
        marca = self.marca or 'Equipo'
        modelo = self.modelo or 'Sin Modelo'
        num_serie = self.num_serie or 'N/A'
        return f"{marca} {modelo} (S/N: {num_serie})"

class Asignacion(models.Model):
    id_asignacion = models.AutoField(db_column='ID_Asignacion', primary_key=True)
    # Mantiene DO_NOTHING por la nota de `inspectdb` / DB existente.
    rut_institucion_receptora = models.ForeignKey(Institucion, models.DO_NOTHING, db_column='RUT_Institucion_Receptora')
    fecha_solicitud = models.DateField(db_column='Fecha_Solicitud', auto_now_add=True)
    cantidad_solicitada = models.IntegerField(db_column='Cantidad_Solicitada')
    estado = models.CharField(db_column='Estado', max_length=9)

    class Meta:
        db_table = 'asignacion'

    def __str__(self):
        return f"Asignación #{self.id_asignacion} para {self.rut_institucion_receptora.nombre}"

class DetalleAsignacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_asignacion = models.ForeignKey(Asignacion, models.CASCADE, db_column='ID_Asignacion')
    id_equipo = models.OneToOneField(Equipo, models.CASCADE, db_column='ID_Equipo')
    fecha_entrega = models.DateField(db_column='Fecha_Entrega', blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)

    class Meta:
        db_table = 'detalle_asignacion'

    def __str__(self):
        return f"Detalle de Equipo #{self.id_equipo.id_equipo} en Asignación #{self.id_asignacion.id_asignacion}"

class Reacondicionamiento(models.Model):
    # CORRECCIÓN: Si se elimina el Equipo, el registro de Reacondicionamiento se elimina (CASCADE).
    id_equipo = models.OneToOneField(Equipo, models.CASCADE, db_column='ID_Equipo', primary_key=True)
    # CORRECCIÓN: Si se elimina el Técnico, se establece el campo a NULL (SET_NULL)
    # dado que el campo es opcional (blank=True, null=True). Se usa 'Usuario' para referenciar el modelo custom.
    id_tecnico = models.ForeignKey(Usuario, models.SET_NULL, db_column='ID_Tecnico', blank=True, null=True)
    taller_asignado = models.CharField(db_column='Taller_Asignado', max_length=150, blank=True, null=True)
    fecha_inicio = models.DateField(db_column='Fecha_Inicio', blank=True, null=True)
    fecha_fin = models.DateField(db_column='Fecha_Fin', blank=True, null=True)
    acciones_realizadas = models.TextField(db_column='Acciones_Realizadas', blank=True, null=True)
    estado_final = models.CharField(db_column='Estado_Final', max_length=20)
    evidencia_final = models.ImageField(upload_to='reacondicionamiento/', blank=True, null=True, verbose_name="Foto del trabajo final")

    class Meta:
        db_table = 'reacondicionamiento'

    def __str__(self):
        return f"Reacondicionamiento para {self.id_equipo}"

class Soporte(models.Model):
    id_soporte = models.AutoField(db_column='ID_Soporte', primary_key=True)
    # Si se elimina la Asignación, se eliminan los Soportes (CASCADE).
    id_asignacion = models.ForeignKey(
        Asignacion,
        models.CASCADE,
        db_column='ID_Asignacion'
    )
    # CORRECCIÓN: Si se elimina el Técnico, se establece el campo a NULL (SET_NULL)
    # dado que el campo es opcional (blank=True, null=True). Se usa 'Usuario' para referenciar el modelo custom.
    id_tecnico = models.ForeignKey(Usuario, models.SET_NULL, db_column='ID_Tecnico', blank=True, null=True)
    tipo = models.CharField(db_column='Tipo', max_length=12)
    fecha_evento = models.DateField(db_column='Fecha_Evento', auto_now_add=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    resolucion = models.TextField(db_column='Resolucion', blank=True, null=True)

    class Meta:
        db_table = 'soporte'
    
    def __str__(self):
        return f"Soporte #{self.id_soporte} ({self.tipo}) para Asignación #{self.id_asignacion.id_asignacion}"