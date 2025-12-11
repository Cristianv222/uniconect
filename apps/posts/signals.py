"""
Signals para el módulo de posts
Manejo automático de menciones, hashtags y notificaciones
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F

from .models import (
    Post, PostImage, PostVideo, PostMention, 
    Hashtag, PostHashtag, PostReport
)


# ============================================================================
# SIGNALS DE POST
# ============================================================================

@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se guarda un post
    - Procesa menciones
    - Procesa hashtags
    - Crea notificaciones
    """
    if created:
        # Procesar menciones
        process_mentions(instance)
        
        # Procesar hashtags
        process_hashtags(instance)
        
        # Crear notificación si es un post compartido
        if instance.shared_post:
            create_share_notification(instance)
    else:
        # Si se editó, actualizar menciones y hashtags
        # Primero eliminar los anteriores
        instance.mentions.all().delete()
        instance.post_hashtags.all().delete()
        
        # Procesar de nuevo
        process_mentions(instance)
        process_hashtags(instance)


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    """
    Se ejecuta cuando se elimina un post
    - Actualiza contadores de hashtags
    - Limpia archivos de media
    """
    # Actualizar contadores de hashtags
    for post_hashtag in instance.post_hashtags.all():
        hashtag = post_hashtag.hashtag
        hashtag.posts_count = F('posts_count') - 1
        hashtag.save(update_fields=['posts_count'])


# ============================================================================
# SIGNALS DE MEDIA
# ============================================================================

@receiver(post_save, sender=PostImage)
def image_saved(sender, instance, created, **kwargs):
    """
    Actualiza el indicador has_images del post
    """
    if created:
        instance.post.has_images = True
        instance.post.save(update_fields=['has_images'])


@receiver(post_delete, sender=PostImage)
def image_deleted(sender, instance, **kwargs):
    """
    Actualiza el indicador has_images del post
    """
    post = instance.post
    if not post.images.exists():
        post.has_images = False
        post.save(update_fields=['has_images'])


@receiver(post_save, sender=PostVideo)
def video_saved(sender, instance, created, **kwargs):
    """
    Actualiza el indicador has_videos del post
    """
    if created:
        instance.post.has_videos = True
        instance.post.save(update_fields=['has_videos'])


@receiver(post_delete, sender=PostVideo)
def video_deleted(sender, instance, **kwargs):
    """
    Actualiza el indicador has_videos del post
    """
    post = instance.post
    if not post.videos.exists():
        post.has_videos = False
        post.save(update_fields=['has_videos'])


# ============================================================================
# SIGNALS DE REPORTES
# ============================================================================

@receiver(post_save, sender=PostReport)
def report_saved(sender, instance, created, **kwargs):
    """
    Notifica a moderadores sobre reportes nuevos
    """
    if created:
        # Aquí se podría enviar notificación a moderadores
        pass


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def process_mentions(post):
    """
    Procesa menciones en el contenido del post
    """
    from apps.authentication.models import User
    
    mentions = post.extract_mentions()
    
    for username in mentions:
        try:
            user = User.objects.get(username=username)
            # Crear mención si no existe
            PostMention.objects.get_or_create(
                post=post,
                user=user
            )
            
            # Crear notificación
            try:
                from apps.notifications.utils import create_notification
                create_notification(
                    recipient=user,
                    sender=post.author,
                    notification_type='post_mention',
                    text=f'{post.author.get_full_name()} te mencionó en una publicación',
                    link=post.get_absolute_url(),
                    related_object_type='post',
                    related_object_id=post.id
                )
            except ImportError:
                pass
        except User.DoesNotExist:
            # Usuario no existe, ignorar
            pass


def process_hashtags(post):
    """
    Procesa hashtags en el contenido del post
    """
    hashtags = post.extract_hashtags()
    
    for tag_name in hashtags:
        # Normalizar: convertir a minúsculas
        tag_name = tag_name.lower()
        
        # Obtener o crear hashtag
        hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
        
        # Crear relación si no existe
        post_hashtag, created = PostHashtag.objects.get_or_create(
            post=post,
            hashtag=hashtag
        )
        
        if created:
            # Incrementar contador
            hashtag.posts_count = F('posts_count') + 1
            hashtag.save(update_fields=['posts_count', 'last_used'])


def create_share_notification(post):
    """
    Crea notificación cuando alguien comparte un post
    """
    if post.shared_post and post.shared_post.author != post.author:
        try:
            from apps.notifications.utils import create_notification
            create_notification(
                recipient=post.shared_post.author,
                sender=post.author,
                notification_type='post_share',
                text=f'{post.author.get_full_name()} compartió tu publicación',
                link=post.get_absolute_url(),
                related_object_type='post',
                related_object_id=post.id
            )
        except ImportError:
            pass


# ============================================================================
# SIGNAL PARA ACTUALIZAR CONTADORES
# ============================================================================

def update_post_counters(post_id):
    """
    Actualiza los contadores de un post
    Útil para llamar desde otras apps (likes, comments)
    """
    try:
        post = Post.objects.get(id=post_id)
        
        # Importar dinámicamente para evitar circular imports
        try:
            from apps.likes.models import Like
            post.likes_count = Like.objects.filter(
                content_type__model='post',
                object_id=post.id
            ).count()
        except ImportError:
            pass
        
        try:
            from apps.comments.models import Comment
            post.comments_count = Comment.objects.filter(post=post).count()
        except ImportError:
            pass
        
        post.shares_count = Post.objects.filter(shared_post=post).count()
        
        post.save(update_fields=['likes_count', 'comments_count', 'shares_count'])
    except Post.DoesNotExist:
        pass