import os
import django
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Charger les variables d'environnement
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# Définit le module de configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoApp.settings")

# Charge Django avant d'importer quoi que ce soit d'autre
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})