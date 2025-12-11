"""
Modelos de publicaciones para UnicoNet
Sistema completo de posts con imágenes, videos, menciones y privacidad
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.urls import reverse
import re


class Post(models.Model):
    """
    Publicación de usuario
    Puede contener texto, imágenes, videos, menciones y hashtags
    """
    
    PRIVACY_CHOICES = [
        ('public', 'Público'),
        ('friends', 'Solo amigos'),
        ('private', 'Solo yo'),
    ]
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('autor')
    )
    
    content = models.TextField(
        _('contenido'),
        max_length=5000,
        help_text=_('Escribe algo...')
    )
    
    privacy = models.CharField(
        _('privacidad'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='friends'
    )
    
    # Ubicación opcional
    location = models.CharField(
        _('ubicación'),
        max_length=200,
        blank=True,
        help_text=_('Ciudad, País')
    )
    
    # Estado de ánimo opcional
    feeling = models.CharField(
        _('sentimiento'),
        max_length=50,
        blank=True,
        choices=[
            ('happy', '😊 Feliz'),
            ('excited', '🤩 Emocionado'),
            ('loved', '🥰 Enamorado'),
            ('sad', '😢 Triste'),
            ('angry', '😠 Enojado'),
            ('tired', '😴 Cansado'),
            ('blessed', '🙏 Bendecido'),
            ('motivated', '💪 Motivado'),
            ('grateful', '🙌 Agradecido'),
            ('confused', '😕 Confundido'),
        ]
    )
    
    # Indicadores de contenido
    has_images = models.BooleanField(_('tiene imágenes'), default=False)
    has_videos = models.BooleanField(_('tiene videos'), default=False)
    
    # Contadores (se actualizan con signals)
    likes_count = models.PositiveIntegerField(_('me gusta'), default=0)
    comments_count = models.PositiveIntegerField(_('comentarios'), default=0)
    shares_count = models.PositiveIntegerField(_('compartidos'), default=0)
    
    # Si es un post compartido
    shared_post = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shares',
        verbose_name=_('post compartido')
    )
    
    # Estado del post
    is_edited = models.BooleanField(_('editado'), default=False)
    is_pinned = models.BooleanField(_('fijado'), default=False)
    is_archived = models.BooleanField(_('archivado'), default=False)
    
    # Fechas
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    edited_at = models.DateTimeField(_('editado en'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('publicación')
        verbose_name_plural = _('publicaciones')
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['privacy', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.author.username}: {content_preview}"
    
    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Si se está editando (no es la primera vez)
        if self.pk and self._state.adding is False:
            original = Post.objects.get(pk=self.pk)
            if original.content != self.content:
                self.is_edited = True
                self.edited_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Actualizar indicadores de contenido
        self.has_images = self.images.exists()
        self.has_videos = self.videos.exists()
        if self.pk:
            Post.objects.filter(pk=self.pk).update(
                has_images=self.has_images,
                has_videos=self.has_videos
            )
    
    @property
    def is_shared(self):
        """Verifica si este post es un compartido"""
        return self.shared_post is not None
    
    def extract_mentions(self):
        """
        Extrae menciones (@username) del contenido
        Retorna lista de usernames mencionados
        """
        pattern = r'@(\w+)'
        return re.findall(pattern, self.content)
    
    def extract_hashtags(self):
        """
        Extrae hashtags (#hashtag) del contenido
        Retorna lista de hashtags
        """
        pattern = r'#(\w+)'
        return re.findall(pattern, self.content)
    
    def can_view(self, user):
        """
        Verifica si un usuario puede ver este post
        """
        # El autor siempre puede ver
        if self.author == user:
            return True
        
        # Posts archivados solo los ve el autor
        if self.is_archived:
            return False
        
        # Post público
        if self.privacy == 'public':
            return True
        
        # Post privado
        if self.privacy == 'private':
            return False
        
        # Post para amigos
        if self.privacy == 'friends':
            from apps.friends.models import are_friends
            return are_friends(self.author, user)
        
        return False
    
    def can_edit(self, user):
        """Verifica si un usuario puede editar este post"""
        return self.author == user
    
    def can_delete(self, user):
        """Verifica si un usuario puede eliminar este post"""
        return self.author == user


class PostImage(models.Model):
    """
    Imagen adjunta a un post
    Un post puede tener múltiples imágenes
    """
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('publicación')
    )
    
    image = models.ImageField(
        _('imagen'),
        upload_to='posts/images/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
            )
        ]
    )
    
    caption = models.CharField(
        _('descripción'),
        max_length=200,
        blank=True
    )
    
    order = models.PositiveSmallIntegerField(
        _('orden'),
        default=0,
        help_text=_('Orden de visualización de la imagen')
    )
    
    uploaded_at = models.DateTimeField(_('subido'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('imagen de publicación')
        verbose_name_plural = _('imágenes de publicación')
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Imagen de {self.post.author.username} - {self.uploaded_at.strftime('%Y-%m-%d')}"


class PostVideo(models.Model):
    """
    Video adjunto a un post
    Un post puede tener múltiples videos
    """
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name=_('publicación')
    )
    
    video = models.FileField(
        _('video'),
        upload_to='posts/videos/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']
            )
        ]
    )
    
    thumbnail = models.ImageField(
        _('miniatura'),
        upload_to='posts/thumbnails/%Y/%m/%d/',
        blank=True,
        null=True
    )
    
    caption = models.CharField(
        _('descripción'),
        max_length=200,
        blank=True
    )
    
    duration = models.PositiveIntegerField(
        _('duración'),
        blank=True,
        null=True,
        help_text=_('Duración en segundos')
    )
    
    order = models.PositiveSmallIntegerField(
        _('orden'),
        default=0
    )
    
    uploaded_at = models.DateTimeField(_('subido'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('video de publicación')
        verbose_name_plural = _('videos de publicación')
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Video de {self.post.author.username} - {self.uploaded_at.strftime('%Y-%m-%d')}"


class PostMention(models.Model):
    """
    Mención de usuario en un post
    Se crea automáticamente al detectar @username
    """
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='mentions',
        verbose_name=_('publicación')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentioned_in_posts',
        verbose_name=_('usuario mencionado')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('mención en publicación')
        verbose_name_plural = _('menciones en publicaciones')
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"@{self.user.username} mencionado en post de {self.post.author.username}"


class Hashtag(models.Model):
    """
    Hashtag usado en posts
    Se crea automáticamente al detectar #hashtag
    """
    
    name = models.CharField(
        _('nombre'),
        max_length=100,
        unique=True,
        db_index=True
    )
    
    posts_count = models.PositiveIntegerField(
        _('publicaciones'),
        default=0
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    last_used = models.DateTimeField(_('último uso'), auto_now=True)
    
    class Meta:
        verbose_name = _('hashtag')
        verbose_name_plural = _('hashtags')
        ordering = ['-posts_count', 'name']
    
    def __str__(self):
        return f"#{self.name}"


class PostHashtag(models.Model):
    """
    Relación entre post y hashtag
    """
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='post_hashtags',
        verbose_name=_('publicación')
    )
    
    hashtag = models.ForeignKey(
        Hashtag,
        on_delete=models.CASCADE,
        related_name='hashtag_posts',
        verbose_name=_('hashtag')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('hashtag de publicación')
        verbose_name_plural = _('hashtags de publicación')
        unique_together = ['post', 'hashtag']
        indexes = [
            models.Index(fields=['hashtag', '-created_at']),
        ]
    
    def __str__(self):
        return f"#{self.hashtag.name} en post de {self.post.author.username}"


class PostReport(models.Model):
    """
    Reporte de contenido inapropiado
    """
    
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Acoso'),
        ('hate_speech', 'Discurso de odio'),
        ('violence', 'Violencia'),
        ('nudity', 'Desnudez o contenido sexual'),
        ('false_info', 'Información falsa'),
        ('self_harm', 'Autolesión o suicidio'),
        ('other', 'Otro'),
    ]
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('publicación')
    )
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_reports',
        verbose_name=_('reportador')
    )
    
    reason = models.CharField(
        _('razón'),
        max_length=20,
        choices=REASON_CHOICES
    )
    
    description = models.TextField(
        _('descripción'),
        max_length=500,
        blank=True,
        help_text=_('Detalles adicionales del reporte')
    )
    
    is_reviewed = models.BooleanField(_('revisado'), default=False)
    is_valid = models.BooleanField(_('válido'), default=False)
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
        verbose_name=_('revisado por')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    reviewed_at = models.DateTimeField(_('revisado en'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('reporte de publicación')
        verbose_name_plural = _('reportes de publicaciones')
        ordering = ['-created_at']
        unique_together = ['post', 'reporter']
        indexes = [
            models.Index(fields=['is_reviewed', '-created_at']),
        ]
    
    def __str__(self):
        return f"Reporte de {self.reporter.username} - {self.get_reason_display()}"