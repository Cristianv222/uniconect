"""
URL Configuration para UnicoNet
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # Apps de UnicoNet
    path('auth/', include('apps.authentication.urls')),
    path('users/', include('apps.users.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('posts/', include('apps.posts.urls')),
    path('comments/', include('apps.comments.urls')),
    path('likes/', include('apps.likes.urls')),
    path('friends/', include('apps.friends.urls')),
    path('groups/', include('apps.groups.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('messages/', include('apps.messages.urls')),
    path('feed/', include('apps.feed.urls')),
    path('events/', include('apps.events.urls')),
    
    # API endpoints (opcional - para DRF)
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/profiles/', include('apps.profiles.urls')),
    path('api/v1/posts/', include('apps.posts.urls')),
    path('api/v1/comments/', include('apps.comments.urls')),
    path('api/v1/likes/', include('apps.likes.urls')),
    path('api/v1/friends/', include('apps.friends.urls')),
    path('api/v1/groups/', include('apps.groups.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/messages/', include('apps.messages.urls')),
    path('api/v1/feed/', include('apps.feed.urls')),
    path('api/v1/events/', include('apps.events.urls')),
    
    # Pagina principal
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
]

# Configuracion de admin
admin.site.site_header = 'UnicoNet Admin'
admin.site.site_title = 'UnicoNet Admin Portal'
admin.site.index_title = 'Bienvenido al panel de administracion de UnicoNet'

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Handler de errores personalizados (opcional)
handler404 = 'apps.authentication.views.handler404'
handler500 = 'apps.authentication.views.handler500'
handler403 = 'apps.authentication.views.handler403'
handler400 = 'apps.authentication.views.handler400'