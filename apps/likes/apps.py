"""
Configuración de la app de likes
"""
from django.apps import AppConfig


class LikesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.likes'
    verbose_name = 'Sistema de Likes'
    
    def ready(self):
        """
        Importar signals cuando la app esté lista
        """
        try:
            import apps.likes.signals
        except ImportError:
            pass