"""Perfil privado: edición explícita sin permitir cambio de rol o privilegios."""
from rest_framework import serializers
from .models import User

class PersonalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'default_address', 'default_commune']

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('El nombre es obligatorio.')
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('El apellido es obligatorio.')
        return value.strip()

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError('Solo se permiten los campos del perfil personal.')
        return attrs

    def validate_phone(self, value):
        if value and (sum(c.isdigit() for c in value) < 8 or not all(c in '+0123456789 -()' for c in value)):
            raise serializers.ValidationError('Ingresa un teléfono válido de al menos 8 caracteres.')
        return value
