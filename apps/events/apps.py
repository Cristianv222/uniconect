# Archivo apps.py para authentication
from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.events'
    verbose_name = 'Eventos'