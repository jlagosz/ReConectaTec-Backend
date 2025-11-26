"""
URL configuration for proyectoBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
Definiciones de URL para el proyecto proyectoBackend.

Este archivo enruta las URLs a las vistas correspondientes definidas
en la aplicación app1Backend.
"""
"""
URL configuration for proyectoBackend project.

Definiciones de URL para el proyecto proyectoBackend.
Este archivo enruta las URLs a las vistas correspondientes definidas
en la aplicación app1Backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app1Backend import views
from rest_framework.routers import DefaultRouter
from app1Backend import api_views

# Configuración del Router de la API
router = DefaultRouter()
router.register(r'instituciones', api_views.InstitucionViewSet)
router.register(r'usuarios', api_views.UsuarioViewSet)
router.register(r'donaciones', api_views.DonacionViewSet)
router.register(r'equipos', api_views.EquipoViewSet)
router.register(r'asignaciones', api_views.AsignacionViewSet)
router.register(r'reacondicionamientos', api_views.ReacondicionamientoViewSet)
router.register(r'soportes', api_views.SoporteViewSet)

urlpatterns = [
    # ----------------------------------------------------
    # 1. RUTAS DE ADMINISTRACIÓN Y AUTENTICACIÓN
    # ----------------------------------------------------
    path('admin/', admin.site.urls),

    # LOGIN: Vista integrada, apunta al template 'app1Backend/login.html'
    path('login/', auth_views.LoginView.as_view(template_name='app1Backend/login.html'), name='login'),

    # LOGOUT: Vista integrada, redirige a la página de login al cerrar sesión
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ----------------------------------------------------
    # 2. RUTA PRINCIPAL (DASHBOARD)
    # ----------------------------------------------------
    # La raíz (/) apunta a la vista que redirige por rol
    path('', views.dashboard_redirect, name='dashboard-redirect'), #cambioo

    # El dashboard de admin ahora vive en /dashboard/
    path('dashboard/', views.dashboard, name='dashboard'), # cambioo

    # ----------------------------------------------------
    # 3. RUTAS CRUD (INSTITUCION) - PK es CharField (RUT) -> Usar <str:pk>
    # ----------------------------------------------------
    path('instituciones/', views.InstitucionListView.as_view(), name='institucion-list'),
    path('instituciones/crear/', views.InstitucionCreateView.as_view(), name='institucion-create'),
    path('instituciones/modificar/<str:pk>/', views.InstitucionUpdateView.as_view(), name='institucion-update'),
    path('instituciones/eliminar/<str:pk>/', views.InstitucionDeleteView.as_view(), name='institucion-delete'),

    # ----------------------------------------------------
    # 4. RUTAS CRUD (USUARIO) - PK es AutoField -> Usar <int:pk>
    # ----------------------------------------------------
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario-list'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='usuario-create'),
    path('usuarios/modificar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='usuario-update'),
    path('usuarios/eliminar/<int:pk>/', views.UsuarioDeleteView.as_view(), name='usuario-delete'),

    # ----------------------------------------------------
    # 5. RUTAS CRUD (DONACION) - PK es AutoField -> Usar <int:pk>
    # ----------------------------------------------------
    path('donaciones/', views.DonacionListView.as_view(), name='donacion-list'),
    path('donaciones/crear/', views.DonacionCreateView.as_view(), name='donacion-create'),
    path('donaciones/modificar/<int:pk>/', views.DonacionUpdateView.as_view(), name='donacion-update'),
    path('donaciones/eliminar/<int:pk>/', views.DonacionDeleteView.as_view(), name='donacion-delete'),

    # ----------------------------------------------------
    # 6. RUTAS CRUD (EQUIPO) - PK es AutoField -> Usar <int:pk>
    # ----------------------------------------------------
    path('equipos/', views.EquipoListView.as_view(), name='equipo-list'),
    path('equipos/crear/', views.EquipoCreateView.as_view(), name='equipo-create'),
    path('equipos/modificar/<int:pk>/', views.EquipoUpdateView.as_view(), name='equipo-update'),
    path('equipos/eliminar/<int:pk>/', views.EquipoDeleteView.as_view(), name='equipo-delete'),

    # ----------------------------------------------------
    # 7. RUTAS CRUD (ASIGNACION) - PK es AutoField -> Usar <int:pk>
    # ----------------------------------------------------
    path('asignaciones/', views.AsignacionListView.as_view(), name='asignacion-list'),
    path('asignaciones/crear/', views.AsignacionCreateView.as_view(), name='asignacion-create'),
    path('asignaciones/modificar/<int:pk>/', views.AsignacionUpdateView.as_view(), name='asignacion-update'),
    path('asignaciones/eliminar/<int:pk>/', views.AsignacionDeleteView.as_view(), name='asignacion-delete'),

    # ----------------------------------------------------
    # 8. RUTAS CRUD (REACONDICIONAMIENTO) - PK es AutoField -> Usar <int:pk>
    # ----------------------------------------------------
    path('reacondicionamientos/', views.ReacondicionamientoListView.as_view(), name='reacondicionamiento-list'),
    path('reacondicionamientos/crear/', views.ReacondicionamientoCreateView.as_view(), name='reacondicionamiento-create'),
    path('reacondicionamientos/modificar/<int:pk>/', views.ReacondicionamientoUpdateView.as_view(), name='reacondicionamiento-update'),
    path('reacondicionamientos/eliminar/<int:pk>/', views.ReacondicionamientoDeleteView.as_view(), name='reacondicionamiento-delete'),

    # ----------------------------------------------------
    # 9. RUTAS CRUD (SOPORTE) - PK es AutoField -> Usar <int:pk>
    # ----------------------------------------------------
    path('soportes/', views.SoporteListView.as_view(), name='soporte-list'),
    path('soportes/crear/', views.SoporteCreateView.as_view(), name='soporte-create'),
    path('soportes/modificar/<int:pk>/', views.SoporteUpdateView.as_view(), name='soporte-update'),
    path('soportes/eliminar/<int:pk>/', views.SoporteDeleteView.as_view(), name='soporte-delete'),

    # --- RUTA PARA LA API ---
    path('api/', include((router.urls, 'api'), namespace='api')),
]