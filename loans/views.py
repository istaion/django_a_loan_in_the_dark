from django.views.generic import CreateView, TemplateView, DetailView, UpdateView
from loans.models import Loan
from loans.forms import LoanForm
import requests
import os
from django.conf import settings
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from accounts.models import CustomUser
from django.contrib import messages
import plotly.express as px
import plotly.utils
import json
import pandas as pd

class LoanCreateView(CreateView):
    model = Loan
    template_name = "loans/create_loan.html"
    form_class = LoanForm
    success_url = reverse_lazy("accounts:user_dashboard")

    def form_valid(self, form):
        """
        Méthode appelée si le formulaire est valide.
        1. Envoie les données du formulaire à l'API externe.
        2. Si succès, enregistre l'objet Loan en base de données.
        """
        user_info = self.request.session.get('user_info')
        user = get_object_or_404(CustomUser, id=user_info['id'])
        token = user.api_token
        headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        api_url = os.getenv("API_BASE_URL", settings.API_BASE_URL) + "/loans/create_loan"
        django_data = form.cleaned_data
        django_data["user_email"] = user.email

        try:
            response = requests.post(api_url, json=django_data, headers=headers)
            data = response.json()

            if response.status_code == 201:
                form.instance.user = user
                for key, value in data.items():
                    setattr(form.instance, key, value)

                return super().form_valid(form)
            else:
                return JsonResponse({"error": data}, status=response.status_code)

        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    def form_invalid(self, form):
        """
        Méthode appelée si le formulaire est invalide.
        """
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"errors": form.errors}, status=400)
        return super().form_invalid(form)
    
class LoanUpdateView(UpdateView):
    model = Loan
    template_name = "loans/loan_update.html"
    form_class = LoanForm
    success_url = reverse_lazy("accounts:user_dashboard")
    
    def get_form(self, form_class=None):
        """On utilise directement l'instance pour initialiser le formulaire"""
        form_class = self.get_form_class()
        loan = self.get_object()
        
        # Créer le formulaire avec l'instance ET des données initiales
        form = form_class(instance=loan, initial={
            'state': loan.state,
            'bank': loan.bank,
            'naics': loan.naics,
            'rev_line_cr': '' if loan.rev_line_cr is None else str(loan.rev_line_cr),
            'low_doc': '' if loan.low_doc is None else str(loan.low_doc),
            'new_exist': '' if loan.new_exist is None else str(loan.new_exist),
            'has_franchise': '' if loan.has_franchise is None else str(loan.has_franchise),
            'recession': '' if loan.recession is None else str(loan.recession),
            'urban_rural': '' if loan.urban_rural is None else str(loan.urban_rural),
            'create_job': loan.create_job,
            'retained_job': loan.retained_job,
            'no_emp': loan.no_emp,
            'term': loan.term,
            'gr_appv': loan.gr_appv
        })

        return form

    def form_valid(self, form):
        """
        Méthode appelée si le formulaire est valide.
        1. Envoie les données du formulaire à l'API externe.
        2. Si succès, enregistre l'objet Loan en base de données.
        """
        user_info = self.request.session.get('user_info')
        user = get_object_or_404(CustomUser, id=user_info['id'])
        token = user.api_token
        headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        loan = self.get_object()
        api_url = os.getenv("API_BASE_URL", settings.API_BASE_URL) + f"/loans/update_loan/{loan.id}"
        django_data = form.cleaned_data
        django_data["user_email"] = user.email

        try:
            response = requests.patch(api_url, json=django_data, headers=headers)
            data = response.json()

            if response.status_code == 200:
                form.instance.user = user
                for key, value in data.items():
                    setattr(form.instance, key, value)

                return super().form_valid(form)
            else:
                return JsonResponse({"error": data}, status=response.status_code)

        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    def form_invalid(self, form):
        """
        Méthode appelée si le formulaire est invalide.
        """
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"errors": form.errors}, status=400)
        return super().form_invalid(form)

class LoanUserView(TemplateView):
    template_name = "loans/user_loan.html"

class AdvisorLoanDetailView(DetailView):
    model = Loan
    template_name = 'loans/advisor_loan.html'
    context_object_name = 'loan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        shap_values = loan.shap_values 
        
        # Labels des caractéristiques dans le même ordre que les SHAP values
        features = ["State", "Bank", "NAICS", "Term", "NoEmp", "NewExist", "CreateJob", "RetainedJob", 
                    "UrbanRural", "RevLineCr", "LowDoc", "GrAppv", "Recession", "HasFranchise"]
        df = pd.DataFrame({
            'Feature': features,
            'ShapValue': shap_values
        })
        # Création du graphique avec Plotly
        fig = px.bar(df,
            x=shap_values, 
            y=features, 
            orientation="h", 
            title="Impact des caractéristiques sur la prédiction",
        )

        # Convertir le graphique en JSON
        context["graph_json"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        
        return context

class UpdateStatusLoanView(UpdateView):
    model = Loan
    fields = []
    
    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')
        loan = self.get_object()
        
        if action == 'validate':
            status = 'accepté'  # Correspond à StatusEnum.STATUS_ACCEPT dans l'api
        elif action == 'reject':
            status = 'refusé'   # Correspond à StatusEnum.STATUS_REJECT dans l'api
        else:
            messages.error(request, "Action non reconnue")
            return redirect('loans:advisor_loan', pk=loan.id) 
        
        api_url = os.getenv("API_BASE_URL", settings.API_BASE_URL) + f"/loans/accept_or_refuse_loan/{loan.id}"
        
        try:
            token = self.request.user.api_token
            headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                }
            
            response = requests.put(
                api_url,
                json={"new_status": status},
                headers=headers
            )
            
            if response.status_code == 200:
                loan.status = status
                loan.save()
                messages.success(request, f"Statut du prêt mis à jour : {status}")
            else:
                messages.error(request, f"Erreur lors de la mise à jour : {response.text}")
        
        except Exception as e:
            messages.error(request, f"Erreur de connexion à l'API : {str(e)}")
        
        # Rediriger vers la liste des prêts ou la page de détail
        return redirect('accounts:list_users')
    
    def get_success_url(self):
        return reverse_lazy('accounts:list_users')
