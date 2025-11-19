"""
Context processors para UnicoNet
Hace disponibles variables globales en todos los templates
"""

from django.conf import settings


def site_info(request):
    """
    Agrega informacion del sitio a todos los templates
    """
    return {
        'SITE_NAME': 'UnicoNet',
        'SITE_DESCRIPTION': 'Red Social Universitaria - UPEC',
        'SITE_URL': request.build_absolute_uri('/'),
        'DEBUG': settings.DEBUG,
        'UNICONET_CONFIG': settings.UNICONET_CONFIG,
    }