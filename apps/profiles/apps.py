# apps/profiles/apps.py
from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    verbose_name = 'Perfiles'
    
    def ready(self):
        """Importa los signals cuando la app esté lista"""
        import apps.profiles.signals