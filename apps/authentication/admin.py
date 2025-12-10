"""
Configuración del admin para la app de autenticación
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserInterest, LoginHistory, PasswordResetToken, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para el modelo User
    """
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'user_type', 'career', 'is_active', 'is_verified', 'date_joined'
    ]
    
    list_filter = [
        'is_active', 'is_verified', 'is_staff', 'is_superuser',
        'user_type', 'career', 'date_joined'
    ]
    
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id']
    
    ordering = ['-date_joined']
    
    readonly_fields = ['date_joined', 'last_login', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        (_('Información Académica'), {
            'fields': ('user_type', 'career', 'semester', 'student_id')
        }),
        (_('Permisos'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Fechas Importantes'), {
            'fields': ('date_joined', 'last_login', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'user_type', 'career'
            ),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    """
    Admin para intereses de usuario
    """
    
    list_display = ['user', 'category', 'name', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['user__username', 'user__email', 'name', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'category', 'name')
        }),
        (_('Detalles'), {
            'fields': ('description',)
        }),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """
    Admin para historial de inicios de sesión
    """
    
    list_display = [
        'user', 'login_time', 'ip_address', 
        'device_type', 'location', 'success'
    ]
    
    list_filter = ['success', 'device_type', 'login_time']
    search_fields = ['user__username', 'user__email', 'ip_address', 'location']
    ordering = ['-login_time']
    date_hierarchy = 'login_time'
    readonly_fields = ['login_time']
    
    def has_add_permission(self, request):
        """
        No permitir agregar registros manualmente
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        No permitir editar registros
        """
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin para tokens de recuperación de contraseña
    """
    
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'used_at']
    
    def token_preview(self, obj):
        """
        Muestra solo los primeros 10 caracteres del token
        """
        return f"{obj.token[:10]}..."
    token_preview.short_description = 'Token'
    
    def has_add_permission(self, request):
        """
        No permitir agregar registros manualmente
        """
        return False


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin para tokens de verificación de email
    """
    
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'used_at']
    
    def token_preview(self, obj):
        """
        Muestra solo los primeros 10 caracteres del token
        """
        return f"{obj.token[:10]}..."
    token_preview.short_description = 'Token'
    
    def has_add_permission(self, request):
        """
        No permitir agregar registros manualmente
        """
        return False