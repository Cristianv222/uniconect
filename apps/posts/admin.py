"""
Admin para el módulo de posts
Gestión completa de publicaciones, imágenes, videos, menciones y reportes
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import (
    Post, PostImage, PostVideo, PostMention, 
    Hashtag, PostHashtag, PostReport
)


class PostImageInline(admin.TabularInline):
    """
    Inline para imágenes de post
    """
    model = PostImage
    extra = 1
    fields = ['image', 'caption', 'order', 'image_preview']
    readonly_fields = ['image_preview', 'uploaded_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista previa'


class PostVideoInline(admin.TabularInline):
    """
    Inline para videos de post
    """
    model = PostVideo
    extra = 1
    fields = ['video', 'thumbnail', 'caption', 'duration', 'order', 'thumbnail_preview']
    readonly_fields = ['thumbnail_preview', 'uploaded_at']
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.thumbnail.url
            )
        return '-'
    thumbnail_preview.short_description = 'Miniatura'


class PostMentionInline(admin.TabularInline):
    """
    Inline para menciones en post
    """
    model = PostMention
    extra = 0
    fields = ['user', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True


class PostHashtagInline(admin.TabularInline):
    """
    Inline para hashtags en post
    """
    model = PostHashtag
    extra = 0
    fields = ['hashtag', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin para publicaciones
    """
    list_display = [
        'id', 'author_link', 'content_preview', 'privacy_badge',
        'stats', 'media_indicators', 'is_edited', 'is_pinned', 
        'created_at'
    ]
    list_filter = [
        'privacy', 'is_edited', 'is_pinned', 'is_archived',
        'has_images', 'has_videos', 'created_at'
    ]
    search_fields = [
        'author__username', 'author__email', 'author__first_name',
        'author__last_name', 'content', 'location'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'edited_at', 'likes_count',
        'comments_count', 'shares_count', 'has_images', 'has_videos',
        'mentioned_users', 'extracted_hashtags'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Post', {
            'fields': ('author', 'content', 'privacy')
        }),
        ('Detalles Adicionales', {
            'fields': ('location', 'feeling', 'shared_post')
        }),
        ('Estado', {
            'fields': ('is_pinned', 'is_archived', 'is_edited', 'edited_at')
        }),
        ('Estadísticas', {
            'fields': (
                'likes_count', 'comments_count', 'shares_count',
                'has_images', 'has_videos'
            )
        }),
        ('Análisis de Contenido', {
            'fields': ('mentioned_users', 'extracted_hashtags'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PostImageInline, PostVideoInline, PostMentionInline, PostHashtagInline]
    
    def author_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Autor'
    
    def content_preview(self, obj):
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return preview
    content_preview.short_description = 'Contenido'
    
    def privacy_badge(self, obj):
        colors = {
            'public': '#28a745',
            'friends': '#ffc107',
            'private': '#dc3545',
        }
        icons = {
            'public': '🌍',
            'friends': '👥',
            'private': '🔒',
        }
        color = colors.get(obj.privacy, '#6c757d')
        icon = icons.get(obj.privacy, '❓')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold; white-space: nowrap;">'
            '{} {}</span>',
            color, icon, obj.get_privacy_display()
        )
    privacy_badge.short_description = 'Privacidad'
    
    def stats(self, obj):
        return format_html(
            '<div style="white-space: nowrap;">'
            '❤️ {} | 💬 {} | 🔄 {}'
            '</div>',
            obj.likes_count, obj.comments_count, obj.shares_count
        )
    stats.short_description = 'Estadísticas'
    
    def media_indicators(self, obj):
        indicators = []
        if obj.has_images:
            count = obj.images.count()
            indicators.append(f'🖼️ {count}')
        if obj.has_videos:
            count = obj.videos.count()
            indicators.append(f'🎥 {count}')
        if obj.shared_post:
            indicators.append('🔄')
        return format_html(' '.join(indicators)) if indicators else '-'
    media_indicators.short_description = 'Media'
    
    def mentioned_users(self, obj):
        mentions = obj.extract_mentions()
        if mentions:
            return ', '.join([f'@{m}' for m in mentions])
        return 'Sin menciones'
    mentioned_users.short_description = 'Usuarios mencionados'
    
    def extracted_hashtags(self, obj):
        hashtags = obj.extract_hashtags()
        if hashtags:
            return ', '.join([f'#{h}' for h in hashtags])
        return 'Sin hashtags'
    extracted_hashtags.short_description = 'Hashtags'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author', 'shared_post').prefetch_related(
            'images', 'videos', 'mentions', 'post_hashtags'
        )
    
    actions = ['pin_posts', 'unpin_posts', 'archive_posts', 'unarchive_posts']
    
    def pin_posts(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} post(s) fijado(s).')
    pin_posts.short_description = 'Fijar posts seleccionados'
    
    def unpin_posts(self, request, queryset):
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} post(s) desfijado(s).')
    unpin_posts.short_description = 'Desfijar posts seleccionados'
    
    def archive_posts(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} post(s) archivado(s).')
    archive_posts.short_description = 'Archivar posts seleccionados'
    
    def unarchive_posts(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(request, f'{updated} post(s) desarchivado(s).')
    unarchive_posts.short_description = 'Desarchivar posts seleccionados'


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """
    Admin para imágenes de posts
    """
    list_display = ['id', 'post_link', 'image_preview', 'caption_preview', 'order', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['post__author__username', 'caption', 'post__content']
    readonly_fields = ['uploaded_at', 'image_preview']
    date_hierarchy = 'uploaded_at'
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.id)
    post_link.short_description = 'Post'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista previa'
    
    def caption_preview(self, obj):
        if obj.caption:
            return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
        return '-'
    caption_preview.short_description = 'Descripción'


@admin.register(PostVideo)
class PostVideoAdmin(admin.ModelAdmin):
    """
    Admin para videos de posts
    """
    list_display = ['id', 'post_link', 'thumbnail_preview', 'caption_preview', 'duration', 'order', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['post__author__username', 'caption', 'post__content']
    readonly_fields = ['uploaded_at', 'thumbnail_preview']
    date_hierarchy = 'uploaded_at'
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.id)
    post_link.short_description = 'Post'
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.thumbnail.url
            )
        return '-'
    thumbnail_preview.short_description = 'Miniatura'
    
    def caption_preview(self, obj):
        if obj.caption:
            return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
        return '-'
    caption_preview.short_description = 'Descripción'


@admin.register(PostMention)
class PostMentionAdmin(admin.ModelAdmin):
    """
    Admin para menciones en posts
    """
    list_display = ['id', 'post_link', 'user_link', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__author__username', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.id)
    post_link.short_description = 'Post'
    
    def user_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.user.id])
        return format_html('<a href="{}">@{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuario mencionado'


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    """
    Admin para hashtags
    """
    list_display = ['id', 'name_display', 'posts_count', 'created_at', 'last_used']
    list_filter = ['created_at', 'last_used']
    search_fields = ['name']
    readonly_fields = ['created_at', 'last_used', 'posts_count']
    date_hierarchy = 'created_at'
    ordering = ['-posts_count', 'name']
    
    def name_display(self, obj):
        return format_html('<strong>#{}</strong>', obj.name)
    name_display.short_description = 'Hashtag'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            posts_count_actual=Count('hashtag_posts')
        )


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    """
    Admin para relaciones post-hashtag
    """
    list_display = ['id', 'post_link', 'hashtag_link', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__content', 'hashtag__name', 'post__author__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.id)
    post_link.short_description = 'Post'
    
    def hashtag_link(self, obj):
        url = reverse('admin:posts_hashtag_change', args=[obj.hashtag.id])
        return format_html('<a href="{}">#{}</a>', url, obj.hashtag.name)
    hashtag_link.short_description = 'Hashtag'


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    """
    Admin para reportes de posts
    """
    list_display = [
        'id', 'post_link', 'reporter_link', 'reason_badge',
        'status_badge', 'created_at', 'reviewed_at'
    ]
    list_filter = [
        'reason', 'is_reviewed', 'is_valid', 'created_at', 'reviewed_at'
    ]
    search_fields = [
        'post__author__username', 'reporter__username',
        'description', 'post__content'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('post', 'reporter', 'reason', 'description')
        }),
        ('Revisión', {
            'fields': ('is_reviewed', 'is_valid', 'reviewed_by', 'reviewed_at')
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )
    
    def post_link(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        content_preview = obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
        return format_html('<a href="{}">Post #{}: {}</a>', url, obj.post.id, content_preview)
    post_link.short_description = 'Post reportado'
    
    def reporter_link(self, obj):
        url = reverse('admin:authentication_user_change', args=[obj.reporter.id])
        return format_html('<a href="{}">{}</a>', url, obj.reporter.username)
    reporter_link.short_description = 'Reportado por'
    
    def reason_badge(self, obj):
        colors = {
            'spam': '#ffc107',
            'harassment': '#fd7e14',
            'hate_speech': '#dc3545',
            'violence': '#dc3545',
            'nudity': '#e83e8c',
            'false_info': '#17a2b8',
            'self_harm': '#6f42c1',
            'other': '#6c757d',
        }
        color = colors.get(obj.reason, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold; white-space: nowrap;">{}</span>',
            color, obj.get_reason_display()
        )
    reason_badge.short_description = 'Razón'
    
    def status_badge(self, obj):
        if not obj.is_reviewed:
            return format_html(
                '<span style="background-color: #ffc107; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-weight: bold;">⏳ Pendiente</span>'
            )
        elif obj.is_valid:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-weight: bold;">✅ Válido</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-weight: bold;">❌ No válido</span>'
            )
    status_badge.short_description = 'Estado'
    
    actions = ['mark_as_reviewed_valid', 'mark_as_reviewed_invalid']
    
    def mark_as_reviewed_valid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_reviewed=True,
            is_valid=True,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reporte(s) marcado(s) como válido(s).')
    mark_as_reviewed_valid.short_description = 'Marcar como revisado y válido'
    
    def mark_as_reviewed_invalid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_reviewed=True,
            is_valid=False,
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} reporte(s) marcado(s) como no válido(s).')
    mark_as_reviewed_invalid.short_description = 'Marcar como revisado y no válido'