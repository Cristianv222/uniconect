"""
ASGI config for UnicoNet project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/

Este archivo es necesario para funcionalidades asincronas como:
- WebSockets para chat en tiempo real
- Notificaciones push
- Server-Sent Events (SSE)
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniconet.settings')

# Obtener la aplicacion ASGI de Django
django_asgi_app = get_asgi_application()

# Si necesitas usar Django Channels para WebSockets:
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import apps.messaging.routing

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             apps.messaging.routing.websocket_urlpatterns
#         )
#     ),
# })

# Por ahora, solo usamos la aplicacion HTTP
application = django_asgi_app