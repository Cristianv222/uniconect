# apps/profiles/signals.py
"""
Signals para crear automáticamente perfiles y configuraciones
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, PrivacySettings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un usuario
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_privacy_settings(sender, instance, created, **kwargs):
    """
    Crea configuración de privacidad cuando se crea un usuario
    """
    if created:
        PrivacySettings.objects.create(user=instance)