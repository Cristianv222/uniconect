"""
Configuración de la app friends
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FriendsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.friends'
    verbose_name = _('Amistades')
    
    def ready(self):
        """
        Importar signals cuando la app esté lista
        """
        try:
            import apps.friends.signals
        except ImportError:
            pass