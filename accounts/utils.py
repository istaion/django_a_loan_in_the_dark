import requests
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

class APIClient:
    @staticmethod
    def login(email, password):
        try:
            url = f"{settings.API_BASE_URL}/auth/login"
            
            data = {
                "email": email,
                "password": password
            }
            data_json = json.dumps(data)
            headers = {
                "Accept": "application/json"
            }
            response = requests.post(url, data=data_json, headers=headers)
            
            if response.ok:
                return response.json()
            return None
        except Exception as e:
            print(f"Erreur lors de la connexion : {str(e)}")
            return None

    @staticmethod
    def get_user_info(token):
        try:
            url = f"{settings.API_BASE_URL}/me"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.ok:
                return response.json()
            return None
        except Exception as e:
            print(f"Exception dans get_user_info : {str(e)}")
            return None

    @staticmethod
    def update_password(token, new_password):
        """
        Met à jour le mot de passe d'un utilisateur via l'API.
        
        :param token: Token d'authentification de l'utilisateur.
        :param new_password: Nouveau mot de passe à définir.
        :return: Dictionnaire contenant la réponse de l'API ou None en cas d'erreur.
        """
        try:
            url = f"{settings.API_BASE_URL}/update-password"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            new_password = str(new_password)
            data = json.dumps({"new_password": new_password})
            
            response = requests.put(url, data=data, headers=headers)

            if response.ok:
                return response.json()
            else:
                return {"error": f"Échec de la mise à jour : {response.text}"}
        except Exception as e:
            print(f"Erreur dans update_password : {str(e)}")
            return {"error": str(e)}
