from rest_framework import serializers
from .models import Institucion, Usuario, Donacion, Equipo, Asignacion, Reacondicionamiento, Soporte

class InstitucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institucion
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'apellido', 'email', 'rol', 'fecha_creacion', 'is_active']

class DonacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donacion
        fields = '__all__'

class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'

class AsignacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignacion
        fields = '__all__'

class ReacondicionamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reacondicionamiento
        fields = '__all__'

class SoporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Soporte
        fields = '__all__'