"""Cercanía por Haversine, sin PostGIS ni llamadas externas para el MVP local.

La caja limita la búsqueda al área metropolitana aproximada, no certifica
límites administrativos. La distancia es en línea recta, no tiempo de viaje.
"""
import math
from rest_framework import serializers

SOUTH, NORTH, WEST, EAST = -33.85, -33.1, -71.1, -70.35


def validate_point(lat, lon):
    if not (math.isfinite(lat) and math.isfinite(lon)
            and SOUTH <= lat <= NORTH and WEST <= lon <= EAST):
        raise serializers.ValidationError('Selecciona un punto dentro del área de Santiago.')


class NearbyQuery(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius_km = serializers.FloatField(min_value=1, max_value=30, default=10)

    def validate(self, attrs):
        validate_point(attrs['latitude'], attrs['longitude'])
        if not math.isfinite(attrs['radius_km']):
            raise serializers.ValidationError('Radio inválido.')
        return attrs


def distance_km(lat, lon, other_lat, other_lon):
    a, b = math.radians(lat), math.radians(other_lat)
    h = math.sin((b-a)/2)**2 + math.cos(a)*math.cos(b)*math.sin(math.radians(other_lon-lon)/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(min(1, max(0, h))))


def nearby(qs, data):
    lat, lon, radius = data['latitude'], data['longitude'], data['radius_km']
    # Una preselección indexable evita cargar todos los perfiles de la BD.
    dy = math.degrees(radius / 6371.0088)
    dx = dy / math.cos(math.radians(max(abs(SOUTH), abs(NORTH))))
    qs = qs.filter(map_visible=True, latitude__range=(lat-dy, lat+dy), longitude__range=(lon-dx, lon+dx))
    rows = []
    for profile in qs:
        distance = distance_km(lat, lon, profile.latitude, profile.longitude)
        if distance <= radius:
            profile.distance_km = distance
            rows.append(profile)
    return sorted(rows, key=lambda p: (p.distance_km, p.pk))
