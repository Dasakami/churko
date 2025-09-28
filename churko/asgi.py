import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddleware
from channels.sessions import SessionMiddlewareStack

# Указываем настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'churko.settings')

# Явно инициализируем Django
django.setup()

# Импортируем только после setup()
from rooms import routing
from django.core.asgi import get_asgi_application  # правильно для Django 5.1+

# Получаем ASGI-приложение для HTTP
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        AuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
