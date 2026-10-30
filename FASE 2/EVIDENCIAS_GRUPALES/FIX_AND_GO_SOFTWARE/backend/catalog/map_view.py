"""Documento público del mapa, sin sesiones, tokens ni datos de usuarios.

Las marcas se reciben desde la app por postMessage; nunca se incrustan datos
de usuarios en HTML. Leaflet coloca etiquetas con textContent para evitar HTML.
"""
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_GET


@require_GET
@xframe_options_exempt
def map_document(request):
    response = render(request, 'catalog/map.html', {'tile_url': settings.MAP_TILE_URL})
    # OSM exige Referer web. La política global same-origin de Django lo elimina
    # en las solicitudes a tiles; aquí enviamos solo el origen, nunca datos privados.
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
