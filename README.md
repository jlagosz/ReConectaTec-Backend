# ReConectaTec - Plataforma de Gestión

ReConectaTec es una plataforma web backend desarrollada en Django diseñada para gestionar el ciclo de vida completo de la donación, reacondicionamiento y redistribución de equipos tecnológicos. Su objetivo es reducir la brecha digital en instituciones educativas vulnerables y mitigar el impacto de la basura electrónica (e-waste).

Este proyecto implementa un sistema robusto de seguridad, autenticación y autorización basado en roles (RBAC).

## Características Principales

* **Gestión de Inventario:** Control total sobre donaciones, equipos, estados de reacondicionamiento y asignaciones.
* **Seguridad Robusta:**
  * Autenticación segura con Hashing de contraseñas (PBKDF2).
  * Protección contra ataques CSRF en todos los formularios.
  * Manejo de sesiones con expiración automática por inactividad.
  * Ocultamiento de claves sensibles mediante variables de entorno (.env).
* **Control de Acceso (RBAC):** Sistema de permisos segregados por roles:
  * Administrador: Control total del sistema, usuarios y logística.
  * Técnico: Gestión de inventario físico, reparaciones y soporte.
  * Voluntario: Gestión de entrada de donaciones.
* **Interfaz:** Panel administrativo responsivo basado en Bootstrap 5.

## Tecnologías Utilizadas

* **Backend:** Python 3.13, Django 5.2.6
* **Base de Datos:** MySQL / MariaDB (vía PyMySQL)
* **Seguridad:** python-decouple (Manejo de variables de entorno)
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3

## Requisitos Previos

* Python 3.10 o superior.
* Servidor de Base de Datos MySQL (ej. XAMPP, WAMP o MySQL Server nativo).
* Git.

## Instalación y Configuración

Sigue estos pasos para levantar el proyecto localmente:

### 1. Clonar el repositorio

```
git clone [https://github.com/TU_USUARIO/ReConectaTec-Backend.git](https://github.com/TU_USUARIO/ReConectaTec-Backend.git)
cd ReConectaTec-Backend
```

### 2. Crear y activar el Entorno Virtual

```
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo llamado .env en la raíz del proyecto (al mismo nivel que manage.py) y configura tus credenciales locales. Puedes basarte en el siguiente ejemplo:

```
# Configuración de Django
SECRET_KEY=tu_clave_secreta_segura_aqui
DEBUG=True

# Credenciales de Base de Datos (MySQL)
DB_PASSWORD=tu_password_de_mysql
```

Nota: Asegúrate de que tu usuario de MySQL sea 'root' o ajusta settings.py si usas otro.

### 5. Base de Datos

Asegúrate de que tu servidor MySQL (XAMPP) esté corriendo.

1. Crea una base de datos vacía llamada db_proyecto_backend.
2. Ejecuta las migraciones de Django para crear las tablas:

```
python manage.py migrate
```

### 6. Crear un Superusuario

Para acceder al sistema por primera vez:

```
python manage.py createsuperuser
```

### 7. Ejecutar el Servidor

```
python manage.py runserver
```

Accede a http://127.0.0.1:8000/ en tu navegador.

## Gestión de Usuarios y Roles

El sistema utiliza el email como identificador de usuario.

### Cómo crear usuarios (Roles)

1. Inicia sesión como Administrador.
2. Ve al módulo Usuarios -> Agregar Nuevo Usuario.
3. Rellena los datos y selecciona el rol deseado (Tecnico, Voluntario, Administrador).
4. El sistema aplicará el hash a la contraseña automáticamente.

### Permisos por Rol

| Módulo             | Administrador | Técnico | Voluntario |
| ------------------- | ------------- | -------- | ---------- |
| Dashboard           | Si            | No       | No         |
| Instituciones       | Si            | No       | No         |
| Usuarios            | Si            | No       | No         |
| Donaciones          | Si            | No       | Si         |
| Equipos             | Si            | Si       | No         |
| Reacondicionamiento | Si            | Si       | No         |
| Soporte             | Si            | Si       | No         |
| Asignaciones        | Si            | No       | No         |

## Estructura del Proyecto

* **proyectoBackend/:** Configuración principal (settings.py, urls.py).
* **app1Backend/:** Aplicación principal.
* **templates/app1Backend/:** Plantillas HTML
* **static/:** Archivos CSS, JS e imágenes
