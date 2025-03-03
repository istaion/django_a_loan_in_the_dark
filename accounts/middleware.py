from django.shortcuts import redirect
from django.urls import reverse
import requests
from django.conf import settings
from django.contrib import messages

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des URLs qui ne nécessitent pas d'authentification
        public_paths = [reverse('accounts:login')]
        
        token = request.session.get('token')
        user_info = request.session.get('user_info')

        # Si l'utilisateur n'a pas de token et tente d'accéder à une page protégée
        if request.path not in public_paths and not token:
            messages.warning(request, "Vous devez être connecté.")
            return redirect('accounts:login')

        # Vérifier si le token a déjà été validé récemment pour éviter des appels API inutiles
        if token and not request.session.get('token_valid'):
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{settings.API_BASE_URL}/auth/verify_token", headers=headers)

                if response.status_code == 200:
                    request.session['token_valid'] = True  # Marque le token comme valide
                else:
                    messages.error(request, "Votre session a expiré. Veuillez vous reconnecter.")
                    request.session.flush()  # Supprime la session pour éviter un état incohérent
                    return redirect('accounts:login')

            except requests.RequestException as e:
                print(f"Erreur lors de la vérification du token: {e}")
                messages.error(request, "Impossible de vérifier votre session. Veuillez réessayer.")
                request.session.flush()
                return redirect('accounts:login')
            
            
        admin_paths = []

        if (request.path in admin_paths or request.path.startswith('/loans/advisor/'))and (not user_info or not user_info.get("is_staff")):
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('accounts:dashboard')  # Redirige vers une page normale

        return self.get_response(request)