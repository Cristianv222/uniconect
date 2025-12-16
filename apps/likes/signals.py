"""
Signals para el módulo de likes
Actualiza contadores automáticamente
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like


@receiver(post_save, sender=Like)
def update_likes_count_on_create(sender, instance, created, **kwargs):
    """
    Actualiza el contador de likes cuando se crea un like
    """
    if created:
        post = instance.post
        post.likes_count = post.likes.count()
        post.save(update_fields=['likes_count'])


@receiver(post_delete, sender=Like)
def update_likes_count_on_delete(sender, instance, **kwargs):
    """
    Actualiza el contador de likes cuando se elimina un like
    """
    post = instance.post
    post.likes_count = post.likes.count()
    post.save(update_fields=['likes_count'])