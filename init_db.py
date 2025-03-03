
import json
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoApp.settings')  
django.setup()  
from accounts.models import CustomUser


def init_django_db():
    with open('users_data.json', 'r') as file:
        users_data = json.load(file)
    for user in users_data:
        # Vérifier si l'utilisateur existe déjà pour éviter les doublons
        if not CustomUser.objects.filter(email=user["email"]).exists():
            new_user = CustomUser(
                id=user["id"],  # Assurez-vous que l'ID est unique ou laissé vide pour qu'il soit généré automatiquement
                email=user["email"],
                is_staff=user["is_staff"]
            )
            new_user.set_password("password1234")  # Utiliser set_password pour hacher le mot de passe
            new_user.save()
            print(f"Utilisateur {user['email']} créé avec succès.")
        else:
            print(f"L'utilisateur {user['email']} existe déjà.")

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





# Exécuter la fonction si ce fichier est lancé directement
if __name__ == "__main__":
    init_django_db()



