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
from django.conf import settings
from django.http import HttpResponse
django_asgi_app = get_asgi_application()

# Middleware personnalisé pour gérer les fichiers médias
class MediaMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http' and scope['path'].startswith('/media/'):
            # Gérer la requête des fichiers médias
            file_path = os.path.join(settings.MEDIA_ROOT, scope['path'][len(settings.MEDIA_URL):])
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Créer une réponse asynchrone et envoyer les données du fichier
                response = HttpResponse(content, content_type="image/jpeg")  # ou autre type MIME si nécessaire
                response.status_code = 200
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"image/jpeg")],  # ou autre type MIME
                })
                await send({
                    "type": "http.response.body",
                    "body": content,
                })
                return
            except FileNotFoundError:
                pass  # Si le fichier n'est pas trouvé, continuer avec l'application par défaut
        
        # Si ce n'est pas une requête pour les fichiers médias, appeler l'application ASGI par défaut
        await self.inner(scope, receive, send)

application = ProtocolTypeRouter({
    "http": MediaMiddleware(django_asgi_app),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})