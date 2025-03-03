from django.urls import path
from loans.views import LoanCreateView, LoanUserView, AdvisorLoanDetailView, UpdateStatusLoanView,LoanUpdateView

app_name = 'loans' 

urlpatterns = [
    path('create/', LoanCreateView.as_view(), name='loan_create'),
    path('update/<uuid:pk>/', LoanUpdateView.as_view(), name='loan_update'),
    path('user_loan/', LoanUserView.as_view(), name='user_loan'),
    path('advisor/loan/<uuid:pk>/', AdvisorLoanDetailView.as_view(), name='advisor_loan'),
    path('advisor/loan/<uuid:pk>/update/', UpdateStatusLoanView.as_view(), name='update'),
]