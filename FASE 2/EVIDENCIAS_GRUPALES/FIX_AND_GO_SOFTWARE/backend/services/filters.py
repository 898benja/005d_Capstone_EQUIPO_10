"""Filtros tipados para no convertir entradas incorrectas en errores 500."""
from rest_framework import serializers
from .models import ServiceRequest

class RequestFilters(serializers.Serializer):
    category = serializers.IntegerField(min_value=1, required=False)
    commune = serializers.IntegerField(min_value=1, required=False)
    provider = serializers.IntegerField(min_value=1, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.CharField(required=False)

    def validate_status(self, value):
        items = [v.strip() for v in value.split(',')]
        if any(v not in ServiceRequest.Status.values for v in items):
            raise serializers.ValidationError('Estado desconocido.')
        return value

    def validate(self, attrs):
        if attrs.get('date_from') and attrs.get('date_to') and attrs['date_from'] > attrs['date_to']:
            raise serializers.ValidationError('El rango de fechas está invertido.')
        return attrs
