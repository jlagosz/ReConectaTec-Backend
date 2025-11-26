from rest_framework import viewsets
from .models import Institucion, Usuario, Donacion, Equipo, Asignacion, Reacondicionamiento, Soporte
from .serializers import (
    InstitucionSerializer, UsuarioSerializer, DonacionSerializer, 
    EquipoSerializer, AsignacionSerializer, ReacondicionamientoSerializer, SoporteSerializer
)


class InstitucionViewSet(viewsets.ModelViewSet):
    queryset = Institucion.objects.all()
    serializer_class = InstitucionSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class DonacionViewSet(viewsets.ModelViewSet):
    queryset = Donacion.objects.all()
    serializer_class = DonacionSerializer

class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer

class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all()
    serializer_class = AsignacionSerializer

class ReacondicionamientoViewSet(viewsets.ModelViewSet):
    queryset = Reacondicionamiento.objects.all()
    serializer_class = ReacondicionamientoSerializer

class SoporteViewSet(viewsets.ModelViewSet):
    queryset = Soporte.objects.all()
    serializer_class = SoporteSerializer