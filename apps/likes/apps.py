# Archivo apps.py para authentication
from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.likes'
    verbose_name = 'Likes'