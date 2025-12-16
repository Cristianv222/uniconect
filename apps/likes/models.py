"""
Modelos para el sistema de likes de UnicoNet
Gestiona los "me gusta" y reacciones en publicaciones
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Like(models.Model):
    """
    Reacción de un usuario a una publicación
    Soporta múltiples tipos de reacciones
    """
    
    REACTION_CHOICES = [
        ('like', '👍 Me gusta'),
        ('love', '❤️ Me encanta'),
        ('haha', '😂 Me divierte'),
        ('wow', '😮 Me asombra'),
        ('sad', '😢 Me entristece'),
        ('angry', '😠 Me enoja'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('usuario')
    )
    
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('publicación')
    )
    
    reaction_type = models.CharField(
        _('tipo de reacción'),
        max_length=10,
        choices=REACTION_CHOICES,
        default='like'
    )
    
    created_at = models.DateTimeField(
        _('creado'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        verbose_name = _('reacción')
        verbose_name_plural = _('reacciones')
        ordering = ['-created_at']
        unique_together = ('user', 'post')  # Un usuario solo puede tener UNA reacción por post
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['reaction_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} reaccionó con {self.get_reaction_type_display()} al post {self.post.pk}"
    
    def clean(self):
        """
        Validaciones personalizadas
        """
        # No se puede reaccionar a posts archivados
        if self.post.is_archived:
            raise ValidationError(_('No se puede reaccionar a publicaciones archivadas.'))
        
        # Verificar que el usuario puede ver el post
        if not self.post.can_view(self.user):
            raise ValidationError(_('No tienes permiso para reaccionar a esta publicación.'))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_user_reaction(user, post):
    """
    Obtiene la reacción de un usuario a un post
    
    Args:
        user: Usuario
        post: Publicación
    
    Returns:
        Like object o None
    """
    try:
        return Like.objects.get(user=user, post=post)
    except Like.DoesNotExist:
        return None


def has_user_liked_post(user, post):
    """
    Verifica si un usuario ha reaccionado a un post
    
    Args:
        user: Usuario a verificar
        post: Publicación a verificar
    
    Returns:
        bool: True si el usuario ha reaccionado, False en caso contrario
    """
    return Like.objects.filter(user=user, post=post).exists()


def get_post_likes_count(post):
    """
    Obtiene el conteo de reacciones de un post
    
    Args:
        post: Publicación
    
    Returns:
        int: Número de reacciones
    """
    return Like.objects.filter(post=post).count()


def get_post_reactions_summary(post):
    """
    Obtiene un resumen de las reacciones por tipo
    
    Args:
        post: Publicación
    
    Returns:
        dict: {'like': 5, 'love': 3, 'haha': 2, ...}
    """
    from django.db.models import Count
    
    reactions = Like.objects.filter(post=post).values('reaction_type').annotate(
        count=Count('reaction_type')
    ).order_by('-count')
    
    summary = {reaction['reaction_type']: reaction['count'] for reaction in reactions}
    return summary


def get_post_likers(post, limit=None):
    """
    Obtiene la lista de usuarios que reaccionaron a un post
    
    Args:
        post: Publicación
        limit: Límite de usuarios a retornar (opcional)
    
    Returns:
        QuerySet: Usuarios que reaccionaron
    """
    likes = Like.objects.filter(post=post).select_related('user', 'user__profile')
    
    if limit:
        likes = likes[:limit]
    
    return [{'user': like.user, 'reaction': like.reaction_type} for like in likes]


def get_user_liked_posts(user, limit=None):
    """
    Obtiene los posts a los que un usuario ha reaccionado
    
    Args:
        user: Usuario
        limit: Límite de posts a retornar (opcional)
    
    Returns:
        QuerySet: Posts con reacción del usuario
    """
    from apps.posts.models import Post
    
    liked_post_ids = Like.objects.filter(user=user).values_list('post_id', flat=True)
    
    posts = Post.objects.filter(
        id__in=liked_post_ids
    ).select_related(
        'author', 'author__profile'
    ).prefetch_related(
        'images', 'videos'
    ).order_by('-created_at')
    
    if limit:
        posts = posts[:limit]
    
    return posts


def toggle_reaction(user, post, reaction_type='like'):
    """
    Alterna o cambia la reacción de un usuario en un post
    
    Args:
        user: Usuario que reacciona
        post: Publicación
        reaction_type: Tipo de reacción ('like', 'love', 'haha', etc.)
    
    Returns:
        tuple: (reacted: bool, reaction_type: str, reactions_count: int)
            - reacted: True si hay reacción, False si se quitó
            - reaction_type: Tipo de reacción actual (o None si se quitó)
            - reactions_count: Nuevo conteo de reacciones del post
    """
    try:
        # Intentar obtener la reacción existente
        like = Like.objects.get(user=user, post=post)
        
        # Si es la misma reacción, quitarla
        if like.reaction_type == reaction_type:
            like.delete()
            reacted = False
            current_reaction = None
        else:
            # Cambiar a la nueva reacción
            like.reaction_type = reaction_type
            like.save()
            reacted = True
            current_reaction = reaction_type
            
    except Like.DoesNotExist:
        # Crear nueva reacción
        Like.objects.create(user=user, post=post, reaction_type=reaction_type)
        reacted = True
        current_reaction = reaction_type
    
    # Actualizar contador en el post
    reactions_count = get_post_likes_count(post)
    post.likes_count = reactions_count
    post.save(update_fields=['likes_count'])
    
    return reacted, current_reaction, reactions_count


def remove_like(user, post):
    """
    Elimina la reacción de un usuario en un post
    
    Args:
        user: Usuario
        post: Publicación
    
    Returns:
        bool: True si se eliminó, False si no existía
    """
    deleted_count, _ = Like.objects.filter(user=user, post=post).delete()
    
    if deleted_count > 0:
        # Actualizar contador
        post.likes_count = get_post_likes_count(post)
        post.save(update_fields=['likes_count'])
        return True
    
    return False