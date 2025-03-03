from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from loans.models import Loan
from .utils import APIClient
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, View, TemplateView, ListView, UpdateView, DetailView
from accounts.forms import UserCreate, UserFisrtLoginForm, UserUpdate
from django.conf import settings
import os 
import requests
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
import random
import string
from django.core.mail import send_mail

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        email = form.cleaned_data.get('username')  # Récupère l'email
        password = form.cleaned_data.get('password')  # Récupère le mot de passe
        
        try:
            # Essaye de te connecter via l'API
            response = APIClient.login(email, password)
            if response and 'access_token' in response:
                token = response['access_token']
                self.request.session['token'] = token
                user_info = APIClient.get_user_info(response['access_token'])
                User = get_user_model()
                current_user, is_create = User.objects.get_or_create(id=user_info['id'])
                print(current_user)

                # Met à jour le modèle utilisateur avec le token API
                current_user.api_token = token
                current_user.save()
                login(self.request, current_user) 
                print(f"utilisateur authentifié : {self.request.user}")

                # Sauvegarde des informations utilisateur dans la session
                self.request.session['user_info'] = user_info
                self.request.session['user_is_staff'] = user_info.get('is_staff')
                print(user_info)

                if user_info['first_connection']:
                    return redirect('accounts:first_login')

                return redirect('accounts:dashboard')
            else:
                messages.error(self.request, 'Identifiants invalides')
        except Exception as e:
            messages.error(self.request, f"Erreur: {e}")
        
        return redirect('accounts:dashboard')
    
    def get_redirect_url(self):
        redirect('accounts:dashboard')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

class FirstLoginView(View):
    template_name = "accounts/first_login.html"

    def get(self, request):
        form = UserFisrtLoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = UserFisrtLoginForm(request.POST)
        if form.is_valid():
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_new_password")

            if new_password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return render(request, self.template_name, {"form": form})

            token = request.user.api_token  

            response = APIClient.update_password(token, new_password)
            if "error" in response:
                messages.error(request, f"Erreur: {response['error']}")
                return render(request, self.template_name, {"form": form})
            
            request.user.set_password(new_password)
            request.user.first_connection = False
            request.user.save()
            messages.success(request, "Votre mot de passe a été mis à jour avec succès.")
            return redirect("accounts:login") 

        return render(request, self.template_name, {"form": form})

class RedirectDashboardView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('accounts:advisor_dashboard')
        else:
            return redirect('accounts:user_dashboard')
        
class UserDashboardView(TemplateView):
    template_name = 'accounts/client_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = Loan.objects.filter(user=self.request.user).first()
        context['loan'] = loan

        return context

class AdvisorDashboardView(TemplateView):
    template_name = 'accounts/advisor_dashboard.html'


class CreateUserView(CreateView):
    model = CustomUser
    form_class = UserCreate
    template_name = "accounts/create_user.html"
    success_url = reverse_lazy('accounts:advisor_dashboard')

    def generate_password(self, length=12):
        """Génère un mot de passe aléatoire"""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))
    

    def form_valid(self, form):
        token = self.request.user.api_token
        headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        api_url = os.getenv("API_BASE_URL", settings.API_BASE_URL) + "/create_user"
        django_data = form.cleaned_data
        password = self.generate_password()
        django_data["password"] = password
        try:
            response = requests.post(api_url, json=django_data, headers=headers)
            data = response.json()
            if response.status_code == 201:
                form.instance.id = data.get("id")
                form.instance.set_password(password)
                self.send_welcome_email(data.get("email"), password)
                return super().form_valid(form)
            else:
                return JsonResponse({"error": data}, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    def get_redirect_url(self):
        redirect('accounts:dashboard')

    def send_welcome_email(self, email, password):
        """Envoie un email avec les informations de connexion"""
        subject = "Bienvenue sur notre plateforme"
        message = f"Bonjour,\n\nVotre compte a été créé avec succès !\n\nVoici vos identifiants :\nEmail: {email}\nMot de passe: {password}\n\nVeuillez vous connecter et modifier votre mot de passe dès que possible.\n\nCordialement,\nL'équipe."
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [email])

class UserListView(ListView):
    model = CustomUser
    template_name = "accounts/client_list.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_staff =False)
        return queryset

class UserEditProfileView(UpdateView):
    model = CustomUser
    template_name = 'accounts/profil_update.html'
    form_class = UserUpdate
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        token = self.request.user.api_token
        headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        api_url = os.getenv("API_BASE_URL", settings.API_BASE_URL) + "/me/edit"
        django_data = form.cleaned_data
        del django_data["profile_picture"]
        try:
            response = requests.patch(api_url, json=django_data, headers=headers)
            data = response.json()
            if response.status_code == 200:
                return super().form_valid(form)
            else:
                return JsonResponse({"error": data}, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    def get_redirect_url(self):
        redirect('accounts:dashboard')

class UserView(DetailView):
    model = CustomUser
    template_name = 'accounts/profil.html'
    context_object_name = 'user'