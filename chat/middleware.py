class ChatAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/chat/'):

            # Cette condition doit bloquer les requêtes sans token
            if not request.session.get('token') or not request.session.get('user_info'):
                from django.shortcuts import redirect
                return redirect('/accounts/login/?next=' + request.path)
            
            
            from django.contrib.auth import login
            from accounts.models import CustomUser

            if not request.user.is_authenticated:
                user_id = request.session.get('user_info', {}).get('id')
                try:
                    user = CustomUser.objects.get(id=user_id)
                    # Authentifier l'utilisateur pour Django
                    login(request, user)
                    print(f"Utilisateur {user.email} authentifié pour Django")
                except (CustomUser.DoesNotExist, Exception) as e:
                    print(f"Erreur d'authentification: {e}")

        return self.get_response(request)