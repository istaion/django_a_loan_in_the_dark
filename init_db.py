import json
import os
import django
import requests
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoApp.settings')  
django.setup()  
from accounts.models import CustomUser
from news.models import New

API_BASE_URL = settings.API_BASE_URL
LOGIN_ENDPOINT = f"{API_BASE_URL}/auth/login"
LIST_ENDPOINT = f"{API_BASE_URL}/list"

def get_access_token():
    response = requests.post(LOGIN_ENDPOINT, json={
        "email": "vic@staff.fr",
        "password": "password1234"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("❌ Échec de l'authentification")
        return None
    
def fetch_users_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(LIST_ENDPOINT, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Échec de la récupération des utilisateurs")
        return []

def init_django_db():
    access_token = get_access_token()
    if not access_token:
        return
    
    users_data = fetch_users_data(access_token)
    for user in users_data:
        if not CustomUser.objects.filter(email=user["email"]).exists():
            new_user = CustomUser(
                id=user["id"],
                email=user["email"],
                is_staff=user["is_staff"]
            )
            new_user.set_password("password1234")
            new_user.save()
            print(f"✅ Utilisateur {user['email']} créé avec succès.")
        else:
            print(f"🔹 L'utilisateur {user['email']} existe déjà.")

    MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
    image_path_vic = os.path.join(MEDIA_DIR, "vic-picture.jpg")
    vic = CustomUser.objects.filter(email="vic@staff.fr").first()
    image_path_nico = os.path.join(MEDIA_DIR, "nico-picture.jpg")
    nico = CustomUser.objects.filter(email="nico@staff.fr").first()
    image_path_leo = os.path.join(MEDIA_DIR, "leo-picture.jpg")
    leo = CustomUser.objects.filter(email="leo@staff.fr").first()
    user_list = [(vic,image_path_vic, "vic-picture.jpg"),(nico,image_path_nico, "nico-picture.jpg"),(leo, image_path_leo, "leo-picture.jpg")]
    for user, image_path, name in user_list:
        if user:
            with open(image_path, "rb") as image_file:
                user.profile_picture.save(name, image_file, save=True)
            print(f"✅ Photo de profil mise à jour pour {user.email}")
        else:
            print("❌ Utilisateur non trouvé !")

    if not New.objects.filter(title="Les licornes se mettent à la datascience !").exists():
            new_new = New(
                title="Les licornes se mettent à la datascience !",
                author=vic,
                content="Mais c'est long..."
            )
            new_new.save()
            print(f"✅ News créé avec succès.")
    else:
        print(f"🔹 La new existe déjà.")
    new = New.objects.filter(title="Les licornes se mettent à la datascience !").first()
    if new:
        image_path = os.path.join(MEDIA_DIR, "optuna.jpg")
        with open(image_path, "rb") as image_file:
            new.picture.save(name, image_file, save=True)
        print(f"✅ Photo mise à jour pour la news")
    else:
        print("❌ News non trouvé !")

# Exécuter la fonction si ce fichier est lancé directement
if __name__ == "__main__":
    init_django_db()



