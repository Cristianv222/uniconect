"""
Signals para el módulo de friends
Maneja eventos relacionados con amistades, solicitudes y notificaciones
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F

from .models import (
    Friendship, FriendRequest, BlockedUser, 
    get_friends_count
)


# ============================================================================
# SIGNALS DE FRIENDSHIP
# ============================================================================

@receiver(post_save, sender=Friendship)
def friendship_created(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se crea una nueva amistad
    - Actualiza contadores de amigos en perfiles
    - Crea notificación (si existe app de notificaciones)
    """
    if created:
        # Actualizar contadores de amigos
        update_friends_count(instance.user1)
        update_friends_count(instance.user2)
        
        # Crear notificación (si la app existe)
        try:
            from apps.notifications.utils import create_notification
            
            # Encontrar qué usuario aceptó la solicitud
            # (el que no envió la solicitud original)
            friend_request = FriendRequest.objects.filter(
                from_user__in=[instance.user1, instance.user2],
                to_user__in=[instance.user1, instance.user2],
                status='accepted'
            ).first()
            
            if friend_request:
                # Notificar al que envió la solicitud
                sender_user = friend_request.from_user
                accepter_user = friend_request.to_user
                
                create_notification(
                    recipient=sender_user,
                    sender=accepter_user,
                    notification_type='friend_accept',
                    text=f'{accepter_user.get_full_name()} aceptó tu solicitud de amistad',
                    link=f'/profiles/{accepter_user.username}/'
                )
        except ImportError:
            pass  # La app de notificaciones no existe todavía


@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    """
    Se ejecuta cuando se elimina una amistad
    - Actualiza contadores de amigos en perfiles
    """
    update_friends_count(instance.user1)
    update_friends_count(instance.user2)


# ============================================================================
# SIGNALS DE FRIEND REQUEST
# ============================================================================

@receiver(post_save, sender=FriendRequest)
def friend_request_saved(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se crea o actualiza una solicitud de amistad
    """
    if created:
        # Nueva solicitud creada - crear notificación
        try:
            from apps.notifications.utils import create_notification
            
            create_notification(
                recipient=instance.to_user,
                sender=instance.from_user,
                notification_type='friend_request',
                text=f'{instance.from_user.get_full_name()} te envió una solicitud de amistad',
                link=f'/friends/requests/',
                related_object_type='friend_request',
                related_object_id=instance.id
            )
        except ImportError:
            pass
    
    else:
        # Solicitud actualizada
        if instance.status == 'rejected':
            # Solicitud rechazada - opcional: notificar al remitente
            pass
        
        elif instance.status == 'cancelled':
            # Solicitud cancelada - eliminar notificación si existe
            try:
                from apps.notifications.models import Notification
                
                Notification.objects.filter(
                    recipient=instance.to_user,
                    sender=instance.from_user,
                    notification_type='friend_request',
                    related_object_type='friend_request',
                    related_object_id=instance.id
                ).delete()
            except ImportError:
                pass


@receiver(pre_save, sender=FriendRequest)
def friend_request_status_changed(sender, instance, **kwargs):
    """
    Se ejecuta antes de guardar una solicitud
    Detecta cambios de estado
    """
    if instance.pk:  # Solo para actualizaciones
        try:
            old_instance = FriendRequest.objects.get(pk=instance.pk)
            
            # Si el estado cambió de pending a accepted
            if old_instance.status == 'pending' and instance.status == 'accepted':
                # Marcar notificación como leída
                try:
                    from apps.notifications.models import Notification
                    
                    Notification.objects.filter(
                        recipient=instance.to_user,
                        sender=instance.from_user,
                        notification_type='friend_request',
                        related_object_type='friend_request',
                        related_object_id=instance.id
                    ).update(is_read=True)
                except ImportError:
                    pass
        
        except FriendRequest.DoesNotExist:
            pass


# ============================================================================
# SIGNALS DE BLOCKED USER
# ============================================================================

@receiver(post_save, sender=BlockedUser)
def user_blocked(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se bloquea un usuario
    - Elimina amistad si existe
    - Cancela solicitudes pendientes
    """
    if created:
        # Las validaciones ya se hacen en el modelo
        # Aquí podríamos agregar logging o auditoría
        pass


@receiver(post_delete, sender=BlockedUser)
def user_unblocked(sender, instance, **kwargs):
    """
    Se ejecuta cuando se desbloquea un usuario
    """
    # Aquí podríamos agregar logging o auditoría
    pass


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def update_friends_count(user):
    """
    Actualiza el contador de amigos en el perfil del usuario
    """
    try:
        from apps.profiles.models import UserProfile
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.friends_count = get_friends_count(user)
        profile.save(update_fields=['friends_count'])
    except Exception as e:
        # Log del error si es necesario
        print(f"Error actualizando friends_count para {user.username}: {e}")


# ============================================================================
# SIGNALS PARA LIMPIEZA DE DATOS
# ============================================================================

@receiver(post_save, sender=FriendRequest)
def cleanup_old_requests(sender, instance, created, **kwargs):
    """
    Limpia solicitudes antiguas rechazadas o canceladas
    Se ejecuta periódicamente (puedes moverlo a un cron job)
    """
    if not created and instance.status in ['rejected', 'cancelled']:
        from django.utils import timezone
        from datetime import timedelta
        
        # Eliminar solicitudes rechazadas/canceladas con más de 30 días
        cutoff_date = timezone.now() - timedelta(days=30)
        
        FriendRequest.objects.filter(
            status__in=['rejected', 'cancelled'],
            updated_at__lt=cutoff_date
        ).delete()


# ============================================================================
# SIGNALS PARA SUGERENCIAS DE AMISTAD
# ============================================================================

@receiver(post_save, sender=Friendship)
def update_suggestions_on_new_friendship(sender, instance, created, **kwargs):
    """
    Actualiza sugerencias cuando se crea una nueva amistad
    - Elimina sugerencias entre los nuevos amigos
    - Genera nuevas sugerencias basadas en amigos en común
    """
    if created:
        from .models import FriendSuggestion
        from .views import generate_friend_suggestions
        
        # Eliminar sugerencias mutuas (ya son amigos)
        FriendSuggestion.objects.filter(
            user=instance.user1,
            suggested_user=instance.user2
        ).delete()
        
        FriendSuggestion.objects.filter(
            user=instance.user2,
            suggested_user=instance.user1
        ).delete()
        
        # Generar nuevas sugerencias para ambos usuarios
        # (basadas en el nuevo amigo en común)
        try:
            generate_friend_suggestions(instance.user1, limit=5)
            generate_friend_suggestions(instance.user2, limit=5)
        except Exception as e:
            print(f"Error generando sugerencias: {e}")


@receiver(post_save, sender=BlockedUser)
def remove_suggestions_on_block(sender, instance, created, **kwargs):
    """
    Elimina sugerencias cuando se bloquea un usuario
    """
    if created:
        from .models import FriendSuggestion
        
        # Eliminar sugerencias en ambas direcciones
        FriendSuggestion.objects.filter(
            user=instance.blocker,
            suggested_user=instance.blocked
        ).delete()
        
        FriendSuggestion.objects.filter(
            user=instance.blocked,
            suggested_user=instance.blocker
        ).delete()


# ============================================================================
# SIGNALS PARA ESTADÍSTICAS
# ============================================================================

@receiver(post_save, sender=FriendRequest)
def track_friend_request_stats(sender, instance, created, **kwargs):
    """
    Rastrea estadísticas de solicitudes de amistad
    Útil para analytics y métricas de la plataforma
    """
    if created:
        # Aquí podrías enviar datos a un sistema de analytics
        # Por ejemplo: mixpanel, google analytics, etc.
        pass


# ============================================================================
# SIGNALS PARA VALIDACIÓN DE INTEGRIDAD
# ============================================================================

@receiver(post_save, sender=Friendship)
def validate_friendship_integrity(sender, instance, created, **kwargs):
    """
    Valida la integridad de las amistades
    Asegura que no haya duplicados o inconsistencias
    """
    if created:
        # Verificar que no exista la amistad inversa
        inverse_exists = Friendship.objects.filter(
            user1=instance.user2,
            user2=instance.user1
        ).exclude(pk=instance.pk).exists()
        
        if inverse_exists:
            # Eliminar el duplicado
            Friendship.objects.filter(
                user1=instance.user2,
                user2=instance.user1
            ).exclude(pk=instance.pk).delete()


# ============================================================================
# SIGNAL PARA LIMPIAR NOTIFICACIONES HUÉRFANAS
# ============================================================================

@receiver(post_delete, sender=FriendRequest)
def cleanup_request_notifications(sender, instance, **kwargs):
    """
    Elimina notificaciones relacionadas cuando se elimina una solicitud
    """
    try:
        from apps.notifications.models import Notification
        
        Notification.objects.filter(
            notification_type='friend_request',
            related_object_type='friend_request',
            related_object_id=instance.id
        ).delete()
    except ImportError:
        pass


# ============================================================================
# SIGNAL PARA ACTUALIZAR ÚLTIMA ACTIVIDAD
# ============================================================================

@receiver(post_save, sender=FriendRequest)
def update_user_activity(sender, instance, created, **kwargs):
    """
    Actualiza la última actividad del usuario
    """
    if created:
        # Actualizar last_activity en el perfil del usuario
        try:
            from django.utils import timezone
            
            if hasattr(instance.from_user, 'profile'):
                # Si tienes un campo last_activity en UserProfile
                pass
        except Exception:
            pass


# ============================================================================
# SIGNAL PARA CACHE INVALIDATION
# ============================================================================

@receiver(post_save, sender=Friendship)
@receiver(post_delete, sender=Friendship)
def invalidate_friends_cache(sender, instance, **kwargs):
    """
    Invalida el cache de amigos cuando cambia una amistad
    Útil si implementas caching con Redis o Memcached
    """
    try:
        from django.core.cache import cache
        
        # Invalidar cache de ambos usuarios
        cache.delete(f'friends_list_{instance.user1.id}')
        cache.delete(f'friends_list_{instance.user2.id}')
        cache.delete(f'friends_count_{instance.user1.id}')
        cache.delete(f'friends_count_{instance.user2.id}')
    except Exception:
        pass


@receiver(post_save, sender=FriendRequest)
@receiver(post_delete, sender=FriendRequest)
def invalidate_requests_cache(sender, instance, **kwargs):
    """
    Invalida el cache de solicitudes
    """
    try:
        from django.core.cache import cache
        
        cache.delete(f'pending_requests_{instance.to_user.id}')
        cache.delete(f'sent_requests_{instance.from_user.id}')
    except Exception:
        pass