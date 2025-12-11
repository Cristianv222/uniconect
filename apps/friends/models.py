"""
Modelos de amistades para UnicoNet
Gestión de relaciones entre usuarios: amistades, solicitudes y bloqueos
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError


class Friendship(models.Model):
    """
    Modelo de amistad entre dos usuarios
    Una amistad es bidireccional y única
    """
    
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_as_user1',
        verbose_name=_('usuario 1')
    )
    
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_as_user2',
        verbose_name=_('usuario 2')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('amistad')
        verbose_name_plural = _('amistades')
        ordering = ['-created_at']
        unique_together = ['user1', 'user2']
        indexes = [
            models.Index(fields=['user1', '-created_at']),
            models.Index(fields=['user2', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"
    
    def clean(self):
        """
        Validaciones personalizadas
        """
        if self.user1 == self.user2:
            raise ValidationError(_('Un usuario no puede ser amigo de sí mismo.'))
        
        # Asegurar que user1 < user2 para mantener consistencia
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class FriendRequest(models.Model):
    """
    Solicitud de amistad pendiente
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
    ]
    
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friend_requests_sent',
        verbose_name=_('de usuario')
    )
    
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friend_requests_received',
        verbose_name=_('para usuario')
    )
    
    status = models.CharField(
        _('estado'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    message = models.TextField(
        _('mensaje'),
        max_length=200,
        blank=True,
        help_text=_('Mensaje opcional de presentación')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    # Campos para seguimiento
    viewed_at = models.DateTimeField(
        _('visto en'),
        blank=True,
        null=True,
        help_text=_('Cuándo el destinatario vio la solicitud')
    )
    
    responded_at = models.DateTimeField(
        _('respondido en'),
        blank=True,
        null=True,
        help_text=_('Cuándo se respondió a la solicitud')
    )
    
    class Meta:
        verbose_name = _('solicitud de amistad')
        verbose_name_plural = _('solicitudes de amistad')
        ordering = ['-created_at']
        unique_together = ['from_user', 'to_user']
        indexes = [
            models.Index(fields=['to_user', 'status', '-created_at']),
            models.Index(fields=['from_user', 'status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.get_status_display()})"
    
    def clean(self):
        """
        Validaciones personalizadas
        """
        if self.from_user == self.to_user:
            raise ValidationError(_('No puedes enviarte una solicitud de amistad a ti mismo.'))
        
        # Verificar que no exista una amistad ya establecida
        if self.pk is None:  # Solo en creación
            if are_friends(self.from_user, self.to_user):
                raise ValidationError(_('Ya son amigos.'))
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def accept(self):
        """
        Acepta la solicitud de amistad y crea la amistad
        """
        if self.status != 'pending':
            raise ValidationError(_('Esta solicitud ya fue procesada.'))
        
        # Actualizar estado
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        
        # Crear amistad
        user1, user2 = sorted([self.from_user, self.to_user], key=lambda u: u.id)
        friendship = Friendship.objects.create(
            user1=user1,
            user2=user2
        )
        
        # Actualizar contadores en perfiles
        self._update_friend_counts()
        
        return friendship
    
    def reject(self):
        """
        Rechaza la solicitud de amistad
        """
        if self.status != 'pending':
            raise ValidationError(_('Esta solicitud ya fue procesada.'))
        
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
    
    def cancel(self):
        """
        Cancela la solicitud de amistad (solo el remitente)
        """
        if self.status != 'pending':
            raise ValidationError(_('Esta solicitud ya fue procesada.'))
        
        self.status = 'cancelled'
        self.responded_at = timezone.now()
        self.save()
    
    def mark_as_viewed(self):
        """
        Marca la solicitud como vista
        """
        if not self.viewed_at:
            self.viewed_at = timezone.now()
            self.save(update_fields=['viewed_at'])
    
    def _update_friend_counts(self):
        """
        Actualiza los contadores de amigos en los perfiles
        """
        from apps.profiles.models import UserProfile
        
        for user in [self.from_user, self.to_user]:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.friends_count = get_friends_count(user)
            profile.save(update_fields=['friends_count'])


class BlockedUser(models.Model):
    """
    Usuario bloqueado
    Impide la interacción entre dos usuarios
    """
    
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_users',
        verbose_name=_('bloqueador')
    )
    
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by',
        verbose_name=_('bloqueado')
    )
    
    reason = models.CharField(
        _('razón'),
        max_length=50,
        choices=[
            ('spam', 'Spam'),
            ('harassment', 'Acoso'),
            ('inappropriate', 'Contenido inapropiado'),
            ('fake', 'Perfil falso'),
            ('other', 'Otro'),
        ],
        blank=True
    )
    
    blocked_at = models.DateTimeField(_('bloqueado en'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('usuario bloqueado')
        verbose_name_plural = _('usuarios bloqueados')
        ordering = ['-blocked_at']
        unique_together = ['blocker', 'blocked']
        indexes = [
            models.Index(fields=['blocker', '-blocked_at']),
            models.Index(fields=['blocked', '-blocked_at']),
        ]
    
    def __str__(self):
        return f"{self.blocker.username} bloqueó a {self.blocked.username}"
    
    def clean(self):
        """
        Validaciones personalizadas
        """
        if self.blocker == self.blocked:
            raise ValidationError(_('No puedes bloquearte a ti mismo.'))
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Al bloquear, eliminar amistad y solicitudes pendientes
        if self.pk is None:  # Solo en creación
            # Eliminar amistad si existe
            remove_friendship(self.blocker, self.blocked)
            
            # Cancelar solicitudes pendientes en ambas direcciones
            FriendRequest.objects.filter(
                from_user=self.blocker,
                to_user=self.blocked,
                status='pending'
            ).update(status='cancelled', responded_at=timezone.now())
            
            FriendRequest.objects.filter(
                from_user=self.blocked,
                to_user=self.blocker,
                status='pending'
            ).update(status='cancelled', responded_at=timezone.now())
        
        super().save(*args, **kwargs)


class FriendSuggestion(models.Model):
    """
    Sugerencias de amistad
    Basadas en amigos en común, intereses, carrera, etc.
    """
    
    REASON_CHOICES = [
        ('mutual_friends', 'Amigos en común'),
        ('same_career', 'Misma carrera'),
        ('same_semester', 'Mismo semestre'),
        ('common_interests', 'Intereses comunes'),
        ('common_groups', 'Grupos en común'),
        ('profile_view', 'Visitó tu perfil'),
        ('other', 'Otro'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friend_suggestions',
        verbose_name=_('usuario')
    )
    
    suggested_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='suggested_to',
        verbose_name=_('usuario sugerido')
    )
    
    reason = models.CharField(
        _('razón'),
        max_length=30,
        choices=REASON_CHOICES,
        default='mutual_friends'
    )
    
    score = models.FloatField(
        _('puntuación'),
        default=0.0,
        help_text=_('Puntuación de relevancia de la sugerencia (0-1)')
    )
    
    is_dismissed = models.BooleanField(
        _('descartada'),
        default=False,
        help_text=_('El usuario descartó esta sugerencia')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    dismissed_at = models.DateTimeField(_('descartada en'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('sugerencia de amistad')
        verbose_name_plural = _('sugerencias de amistad')
        ordering = ['-score', '-created_at']
        unique_together = ['user', 'suggested_user']
        indexes = [
            models.Index(fields=['user', '-score', '-created_at']),
        ]
    
    def __str__(self):
        return f"Sugerir {self.suggested_user.username} a {self.user.username}"
    
    def dismiss(self):
        """
        Descartar esta sugerencia
        """
        self.is_dismissed = True
        self.dismissed_at = timezone.now()
        self.save()


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def are_friends(user1, user2):
    """
    Verifica si dos usuarios son amigos
    """
    if not user1 or not user2 or user1 == user2:
        return False
    
    user_min, user_max = sorted([user1, user2], key=lambda u: u.id)
    return Friendship.objects.filter(
        user1=user_min,
        user2=user_max
    ).exists()


def get_friends(user):
    """
    Obtiene todos los amigos de un usuario
    """
    from django.db.models import Q
    
    friendships = Friendship.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).select_related('user1', 'user2')
    
    friends = []
    for friendship in friendships:
        friend = friendship.user2 if friendship.user1 == user else friendship.user1
        friends.append(friend)
    
    return friends


def get_friends_count(user):
    """
    Obtiene el número de amigos de un usuario
    """
    from django.db.models import Q
    
    return Friendship.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).count()


def remove_friendship(user1, user2):
    """
    Elimina una amistad entre dos usuarios
    """
    if not user1 or not user2:
        return False
    
    user_min, user_max = sorted([user1, user2], key=lambda u: u.id)
    deleted_count, _ = Friendship.objects.filter(
        user1=user_min,
        user2=user_max
    ).delete()
    
    # Actualizar contadores
    if deleted_count > 0:
        from apps.profiles.models import UserProfile
        
        for user in [user1, user2]:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.friends_count = get_friends_count(user)
            profile.save(update_fields=['friends_count'])
    
    return deleted_count > 0


def is_blocked(blocker, blocked):
    """
    Verifica si un usuario tiene bloqueado a otro
    """
    if not blocker or not blocked:
        return False
    
    return BlockedUser.objects.filter(
        blocker=blocker,
        blocked=blocked
    ).exists()


def has_pending_request(from_user, to_user):
    """
    Verifica si existe una solicitud pendiente entre dos usuarios
    """
    return FriendRequest.objects.filter(
        from_user=from_user,
        to_user=to_user,
        status='pending'
    ).exists()


def get_mutual_friends(user1, user2):
    """
    Obtiene los amigos en común entre dos usuarios
    """
    friends1 = set(get_friends(user1))
    friends2 = set(get_friends(user2))
    return list(friends1 & friends2)


def get_mutual_friends_count(user1, user2):
    """
    Obtiene el número de amigos en común
    """
    return len(get_mutual_friends(user1, user2))