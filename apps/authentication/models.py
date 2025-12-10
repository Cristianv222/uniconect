"""
Modelos de autenticación para UnicoNet
Red Social Universitaria - UPEC
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para el modelo de usuario
    """
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Crea y guarda un usuario regular
        """
        if not email:
            raise ValueError(_('El email es obligatorio'))
        if not username:
            raise ValueError(_('El username es obligatorio'))
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Crea y guarda un superusuario
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('El superusuario debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('El superusuario debe tener is_superuser=True.'))
        
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado para UnicoNet
    """
    
    # Validadores
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_-]{3,30}$',
        message=_('El username debe tener entre 3-30 caracteres. Solo letras, números, guiones y guiones bajos.')
    )
    
    # Sobrescribir campos de PermissionsMixin para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('grupos'),
        blank=True,
        help_text=_('Los grupos a los que pertenece este usuario.'),
        related_name='uniconet_users',
        related_query_name='uniconet_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('permisos de usuario'),
        blank=True,
        help_text=_('Permisos específicos para este usuario.'),
        related_name='uniconet_users',
        related_query_name='uniconet_user',
    )
    
    # Campos principales
    email = models.EmailField(
        _('email'),
        unique=True,
        max_length=255,
        db_index=True,
        error_messages={
            'unique': _('Ya existe un usuario con este email.'),
        }
    )
    
    username = models.CharField(
        _('nombre de usuario'),
        max_length=30,
        unique=True,
        validators=[username_validator],
        db_index=True,
        error_messages={
            'unique': _('Ya existe un usuario con este nombre de usuario.'),
        }
    )
    
    # Información personal básica
    first_name = models.CharField(_('nombre'), max_length=50)
    last_name = models.CharField(_('apellido'), max_length=50)
    
    # Información académica
    CAREER_CHOICES = [
        ('sistemas', 'Ingeniería en Sistemas'),
        ('software', 'Ingeniería en Software'),
        ('electronica', 'Ingeniería Electrónica'),
        ('comercio', 'Comercio Exterior'),
        ('turismo', 'Turismo'),
        ('agroindustria', 'Agroindustria'),
        ('enfermeria', 'Enfermería'),
        ('otro', 'Otro'),
    ]
    
    career = models.CharField(
        _('carrera'),
        max_length=50,
        choices=CAREER_CHOICES,
        blank=True,
        null=True
    )
    
    semester = models.PositiveSmallIntegerField(
        _('semestre'),
        blank=True,
        null=True,
        help_text=_('Semestre actual del estudiante')
    )
    
    student_id = models.CharField(
        _('código de estudiante'),
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Código único de estudiante de UPEC')
    )
    
    # Tipo de usuario
    USER_TYPE_CHOICES = [
        ('student', 'Estudiante'),
        ('teacher', 'Docente'),
        ('admin', 'Administrativo'),
        ('graduate', 'Egresado'),
    ]
    
    user_type = models.CharField(
        _('tipo de usuario'),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    
    # Información de contacto adicional
    phone = models.CharField(
        _('teléfono'),
        max_length=15,
        blank=True,
        null=True
    )
    
    # Estado del usuario
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Designa si este usuario debe ser tratado como activo.')
    )
    
    is_staff = models.BooleanField(
        _('staff'),
        default=False,
        help_text=_('Designa si el usuario puede entrar al sitio de administración.')
    )
    
    is_verified = models.BooleanField(
        _('verificado'),
        default=False,
        help_text=_('Designa si el usuario ha verificado su email.')
    )
    
    # Fechas importantes
    date_joined = models.DateTimeField(_('fecha de registro'), default=timezone.now)
    last_login = models.DateTimeField(_('último inicio de sesión'), blank=True, null=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)
    
    # Configuración del manager
    objects = CustomUserManager()
    
    # Campos requeridos para autenticación
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active', 'is_verified']),
        ]
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """
        Retorna el nombre completo del usuario
        """
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """
        Retorna el nombre corto del usuario
        """
        return self.first_name
    
    @property
    def is_student(self):
        """
        Verifica si el usuario es estudiante
        """
        return self.user_type == 'student'
    
    @property
    def is_teacher(self):
        """
        Verifica si el usuario es docente
        """
        return self.user_type == 'teacher'


class UserInterest(models.Model):
    """
    Intereses de los usuarios
    """
    
    CATEGORY_CHOICES = [
        ('academic', 'Académico'),
        ('sports', 'Deportes'),
        ('arts', 'Arte y Cultura'),
        ('technology', 'Tecnología'),
        ('music', 'Música'),
        ('travel', 'Viajes'),
        ('food', 'Gastronomía'),
        ('reading', 'Lectura'),
        ('gaming', 'Videojuegos'),
        ('other', 'Otro'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interests',
        verbose_name=_('usuario')
    )
    
    category = models.CharField(
        _('categoría'),
        max_length=50,
        choices=CATEGORY_CHOICES
    )
    
    name = models.CharField(
        _('nombre del interés'),
        max_length=100,
        help_text=_('Ejemplo: Programación, Fútbol, Fotografía')
    )
    
    description = models.TextField(
        _('descripción'),
        blank=True,
        help_text=_('Descripción opcional del interés')
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('interés')
        verbose_name_plural = _('intereses')
        ordering = ['category', 'name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class LoginHistory(models.Model):
    """
    Historial de inicios de sesión
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name=_('usuario')
    )
    
    login_time = models.DateTimeField(_('hora de inicio'), auto_now_add=True)
    
    ip_address = models.GenericIPAddressField(
        _('dirección IP'),
        blank=True,
        null=True
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        help_text=_('Información del navegador')
    )
    
    device_type = models.CharField(
        _('tipo de dispositivo'),
        max_length=50,
        blank=True,
        choices=[
            ('desktop', 'Escritorio'),
            ('mobile', 'Móvil'),
            ('tablet', 'Tablet'),
            ('other', 'Otro'),
        ]
    )
    
    location = models.CharField(
        _('ubicación'),
        max_length=100,
        blank=True,
        help_text=_('Ciudad, País')
    )
    
    success = models.BooleanField(
        _('exitoso'),
        default=True,
        help_text=_('Indica si el inicio de sesión fue exitoso')
    )
    
    class Meta:
        verbose_name = _('historial de inicio de sesión')
        verbose_name_plural = _('historial de inicios de sesión')
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"


class PasswordResetToken(models.Model):
    """
    Tokens para recuperación de contraseña
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name=_('usuario')
    )
    
    token = models.CharField(
        _('token'),
        max_length=100,
        unique=True,
        db_index=True
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    expires_at = models.DateTimeField(_('expira'))
    
    is_used = models.BooleanField(
        _('usado'),
        default=False
    )
    
    used_at = models.DateTimeField(
        _('usado en'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('token de recuperación de contraseña')
        verbose_name_plural = _('tokens de recuperación de contraseña')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."
    
    def is_valid(self):
        """
        Verifica si el token es válido
        """
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """
        Marca el token como usado
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save()


class EmailVerificationToken(models.Model):
    """
    Tokens para verificación de email
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens',
        verbose_name=_('usuario')
    )
    
    token = models.CharField(
        _('token'),
        max_length=100,
        unique=True,
        db_index=True
    )
    
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    
    expires_at = models.DateTimeField(_('expira'))
    
    is_used = models.BooleanField(
        _('usado'),
        default=False
    )
    
    used_at = models.DateTimeField(
        _('usado en'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('token de verificación de email')
        verbose_name_plural = _('tokens de verificación de email')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."
    
    def is_valid(self):
        """
        Verifica si el token es válido
        """
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """
        Marca el token como usado
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save()