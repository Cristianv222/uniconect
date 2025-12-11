"""
Admin para el módulo de friends
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    Friendship, FriendRequest, BlockedUser, FriendSuggestion
)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    """
    Admin para amistades
    """
    list_display = ['id', 'user1_link', 'user2_link', 'created_at']
    list_filter = ['created_at']
    search_fields = [
        'user1__username', 'user1__email', 'user1__first_name', 'user1__last_name',
        'user2__username', 'user2__email', 'user2__first_name', 'user2__last_name'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def user1_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.user1.id])
        return format_html('<a href="{}">{}</a>', url, obj.user1.username)
    user1_link.short_description = 'Usuario 1'
    
    def user2_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.user2.id])
        return format_html('<a href="{}">{}</a>', url, obj.user2.username)
    user2_link.short_description = 'Usuario 2'


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    """
    Admin para solicitudes de amistad
    """
    list_display = [
        'id', 'from_user_link', 'to_user_link', 'status_badge',
        'created_at', 'viewed_at', 'responded_at'
    ]
    list_filter = ['status', 'created_at', 'responded_at']
    search_fields = [
        'from_user__username', 'from_user__email',
        'to_user__username', 'to_user__email'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'viewed_at', 'responded_at']
    
    fieldsets = (
        ('Usuarios', {
            'fields': ('from_user', 'to_user')
        }),
        ('Información', {
            'fields': ('status', 'message')
        }),
        ('Seguimiento', {
            'fields': ('created_at', 'updated_at', 'viewed_at', 'responded_at')
        }),
    )
    
    def from_user_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.from_user.id])
        return format_html('<a href="{}">{}</a>', url, obj.from_user.username)
    from_user_link.short_description = 'De'
    
    def to_user_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.to_user.id])
        return format_html('<a href="{}">{}</a>', url, obj.to_user.username)
    to_user_link.short_description = 'Para'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'accepted': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    """
    Admin para usuarios bloqueados
    """
    list_display = ['id', 'blocker_link', 'blocked_link', 'reason', 'blocked_at']
    list_filter = ['reason', 'blocked_at']
    search_fields = [
        'blocker__username', 'blocker__email',
        'blocked__username', 'blocked__email'
    ]
    date_hierarchy = 'blocked_at'
    readonly_fields = ['blocked_at']
    
    def blocker_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.blocker.id])
        return format_html('<a href="{}">{}</a>', url, obj.blocker.username)
    blocker_link.short_description = 'Bloqueador'
    
    def blocked_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.blocked.id])
        return format_html('<a href="{}">{}</a>', url, obj.blocked.username)
    blocked_link.short_description = 'Bloqueado'


@admin.register(FriendSuggestion)
class FriendSuggestionAdmin(admin.ModelAdmin):
    """
    Admin para sugerencias de amistad
    """
    list_display = [
        'id', 'user_link', 'suggested_user_link', 'reason',
        'score', 'is_dismissed', 'created_at'
    ]
    list_filter = ['reason', 'is_dismissed', 'created_at']
    search_fields = [
        'user__username', 'user__email',
        'suggested_user__username', 'suggested_user__email'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'dismissed_at']
    
    def user_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuario'
    
    def suggested_user_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.suggested_user.id])
        return format_html('<a href="{}">{}</a>', url, obj.suggested_user.username)
    suggested_user_link.short_description = 'Usuario sugerido'