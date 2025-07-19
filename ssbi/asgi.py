"""
ASGI config for ssbi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssbi.settings')

# Setup Django
django.setup()

# Import AFTER django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from main.routing import websocket_urlpatterns
from main.utils import JWTAuthMiddleware

# Django ASGI application
django_asgi_app = get_asgi_application()

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
