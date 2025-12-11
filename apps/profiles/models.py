# apps/profiles/models.py
"""
Modelos de perfiles para UnicoNet
Extiende la información del usuario con datos adicionales de perfil
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """
    Perfil extendido del usuario
    Información adicional que no está en el modelo User
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('usuario')
    )
    
    # Información personal adicional
    bio = models.TextField(
        _('biografía'),
        max_length=500,
        blank=True,
        help_text=_('Cuéntanos sobre ti (máximo 500 caracteres)')
    )
    
    birth_date = models.DateField(
        _('fecha de nacimiento'),
        blank=True,
        null=True
    )
    
    gender = models.CharField(
        _('género'),
        max_length=20,
        choices=[
            ('male', 'Masculino'),
            ('female', 'Femenino'),
            ('other', 'Otro'),
            ('prefer_not_to_say', 'Prefiero no decir'),
        ],
        blank=True
    )
    
    location = models.CharField(
        _('ubicación'),
        max_length=100,
        blank=True,
        help_text=_('Ciudad, País')
    )
    
    website = models.URLField(
        _('sitio web'),
        blank=True,
        max_length=200
    )
    
    # Imágenes
    profile_image = models.ImageField(
        _('foto de perfil'),
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Imagen de perfil (recomendado: 500x500px)')
    )
    
    cover_image = models.ImageField(
        _('foto de portada'),
        upload_to='covers/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Imagen de portada (recomendado: 1200x400px)')
    )
    
    # Redes sociales
    facebook_url = models.URLField(_('Facebook'), blank=True, max_length=200)
    twitter_url = models.URLField(_('Twitter/X'), blank=True, max_length=200)
    instagram_url = models.URLField(_('Instagram'), blank=True, max_length=200)
    linkedin_url = models.URLField(_('LinkedIn'), blank=True, max_length=200)
    github_url = models.URLField(_('GitHub'), blank=True, max_length=200)
    
    # Estadísticas (se actualizan automáticamente)
    posts_count = models.PositiveIntegerField(_('publicaciones'), default=0)
    friends_count = models.PositiveIntegerField(_('amigos'), default=0)
    followers_count = models.PositiveIntegerField(_('seguidores'), default=0)
    following_count = models.PositiveIntegerField(_('siguiendo'), default=0)
    
    # Configuración
    is_profile_public = models.BooleanField(
        _('perfil público'),
        default=True,
        help_text=_('Si está desactivado, solo tus amigos pueden ver tu perfil')
    )
    
    show_email = models.BooleanField(
        _('mostrar email'),
        default=False,
        help_text=_('Mostrar email en el perfil público')
    )
    
    show_phone = models.BooleanField(
        _('mostrar teléfono'),
        default=False,
        help_text=_('Mostrar teléfono en el perfil público')
    )
    
    # Fechas
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('perfil de usuario')
        verbose_name_plural = _('perfiles de usuario')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def age(self):
        """Calcula la edad del usuario"""
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class UserSkill(models.Model):
    """
    Habilidades y competencias del usuario
    """
    
    LEVEL_CHOICES = [
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
        ('expert', 'Experto'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name=_('usuario')
    )
    
    name = models.CharField(
        _('habilidad'),
        max_length=100,
        help_text=_('Ejemplo: Python, Photoshop, Marketing Digital')
    )
    
    level = models.CharField(
        _('nivel'),
        max_length=20,
        choices=LEVEL_CHOICES,
        default='intermediate'
    )
    
    years_of_experience = models.PositiveSmallIntegerField(
        _('años de experiencia'),
        blank=True,
        null=True,
        validators=[MaxValueValidator(50)]
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('habilidad')
        verbose_name_plural = _('habilidades')
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.get_level_display()})"


class Education(models.Model):
    """
    Historial educativo del usuario
    """
    
    DEGREE_CHOICES = [
        ('high_school', 'Bachillerato'),
        ('technical', 'Técnico'),
        ('technology', 'Tecnología'),
        ('bachelor', 'Pregrado/Licenciatura'),
        ('master', 'Maestría'),
        ('phd', 'Doctorado'),
        ('certificate', 'Certificación'),
        ('diploma', 'Diplomado'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='education',
        verbose_name=_('usuario')
    )
    
    institution = models.CharField(
        _('institución'),
        max_length=200,
        help_text=_('Nombre de la universidad o institución')
    )
    
    degree = models.CharField(
        _('título'),
        max_length=50,
        choices=DEGREE_CHOICES
    )
    
    field_of_study = models.CharField(
        _('campo de estudio'),
        max_length=100,
        blank=True,
        help_text=_('Ejemplo: Ingeniería de Sistemas, Administración')
    )
    
    start_date = models.DateField(_('fecha de inicio'))
    
    end_date = models.DateField(
        _('fecha de finalización'),
        blank=True,
        null=True
    )
    
    is_current = models.BooleanField(
        _('actual'),
        default=False,
        help_text=_('¿Estás estudiando actualmente aquí?')
    )
    
    grade = models.CharField(
        _('calificación'),
        max_length=50,
        blank=True,
        help_text=_('Ejemplo: 9.5/10, Cum Laude, etc.')
    )
    
    description = models.TextField(
        _('descripción'),
        blank=True,
        max_length=500,
        help_text=_('Actividades, logros, proyectos destacados')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('educación')
        verbose_name_plural = _('educación')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_degree_display()} en {self.institution}"


class WorkExperience(models.Model):
    """
    Experiencia laboral del usuario
    """
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Tiempo completo'),
        ('part_time', 'Medio tiempo'),
        ('freelance', 'Freelance'),
        ('internship', 'Pasantía'),
        ('contract', 'Contrato'),
        ('volunteer', 'Voluntariado'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='work_experience',
        verbose_name=_('usuario')
    )
    
    company = models.CharField(
        _('empresa'),
        max_length=200,
        help_text=_('Nombre de la empresa u organización')
    )
    
    position = models.CharField(
        _('cargo'),
        max_length=100,
        help_text=_('Ejemplo: Desarrollador Full Stack, Gerente de Marketing')
    )
    
    employment_type = models.CharField(
        _('tipo de empleo'),
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    
    location = models.CharField(
        _('ubicación'),
        max_length=100,
        blank=True,
        help_text=_('Ciudad, País o "Remoto"')
    )
    
    start_date = models.DateField(_('fecha de inicio'))
    
    end_date = models.DateField(
        _('fecha de finalización'),
        blank=True,
        null=True
    )
    
    is_current = models.BooleanField(
        _('trabajo actual'),
        default=False,
        help_text=_('¿Trabajas actualmente aquí?')
    )
    
    description = models.TextField(
        _('descripción'),
        blank=True,
        max_length=1000,
        help_text=_('Responsabilidades, logros, proyectos destacados')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('experiencia laboral')
        verbose_name_plural = _('experiencia laboral')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.position} en {self.company}"


class PrivacySettings(models.Model):
    """
    Configuración de privacidad del usuario
    """
    
    PRIVACY_CHOICES = [
        ('public', 'Público'),
        ('friends', 'Solo amigos'),
        ('private', 'Solo yo'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='privacy_settings',
        verbose_name=_('usuario')
    )
    
    # Visibilidad del perfil
    profile_visibility = models.CharField(
        _('visibilidad del perfil'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='public'
    )
    
    email_visibility = models.CharField(
        _('visibilidad del email'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='private'
    )
    
    phone_visibility = models.CharField(
        _('visibilidad del teléfono'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='private'
    )
    
    birth_date_visibility = models.CharField(
        _('visibilidad de fecha de nacimiento'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='friends'
    )
    
    # Posts y contenido
    default_post_privacy = models.CharField(
        _('privacidad por defecto de posts'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='friends',
        help_text=_('Privacidad predeterminada para nuevos posts')
    )
    
    # Amigos
    friend_list_visibility = models.CharField(
        _('visibilidad de lista de amigos'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='friends'
    )
    
    # Mensajería
    who_can_message = models.CharField(
        _('quién puede enviar mensajes'),
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='friends'
    )
    
    # Notificaciones
    email_notifications = models.BooleanField(
        _('notificaciones por email'),
        default=True
    )
    
    push_notifications = models.BooleanField(
        _('notificaciones push'),
        default=True
    )
    
    friend_request_notifications = models.BooleanField(
        _('notificar solicitudes de amistad'),
        default=True
    )
    
    post_like_notifications = models.BooleanField(
        _('notificar "me gusta" en posts'),
        default=True
    )
    
    comment_notifications = models.BooleanField(
        _('notificar comentarios'),
        default=True
    )
    
    mention_notifications = models.BooleanField(
        _('notificar menciones'),
        default=True
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    class Meta:
        verbose_name = _('configuración de privacidad')
        verbose_name_plural = _('configuraciones de privacidad')
    
    def __str__(self):
        return f"Privacidad de {self.user.username}"


class ProfileView(models.Model):
    """
    Registro de visitas a perfiles
    Para estadísticas y sugerencias
    """
    
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_views_made',
        verbose_name=_('visitante')
    )
    
    viewed_profile = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_views_received',
        verbose_name=_('perfil visitado')
    )
    
    viewed_at = models.DateTimeField(_('visto en'), auto_now_add=True)
    
    ip_address = models.GenericIPAddressField(
        _('dirección IP'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('visita de perfil')
        verbose_name_plural = _('visitas de perfil')
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['viewed_profile', '-viewed_at']),
            models.Index(fields=['viewer', '-viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.viewer.username} vio a {self.viewed_profile.username}"