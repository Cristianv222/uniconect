"""
Configuración del admin para likes
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Like
    """
    list_display = [
        'id',
        'user_link',
        'post_link',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'post__content',
    ]
    
    readonly_fields = [
        'created_at',
    ]
    
    list_select_related = [
        'user',
        'post',
        'post__author',
    ]
    
    date_hierarchy = 'created_at'
    
    def user_link(self, obj):
        """Link al usuario"""
        return format_html(
            '<a href="/admin/authentication/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'Usuario'
    
    def post_link(self, obj):
        """Link al post con preview"""
        content_preview = obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
        return format_html(
            '<a href="/admin/posts/post/{}/change/">{}</a>',
            obj.post.id,
            content_preview
        )
    post_link.short_description = 'Publicación'
    
    def has_add_permission(self, request):
        """
        Deshabilitar agregar likes desde el admin
        Los likes solo se crean desde la interfaz
        """
        return False