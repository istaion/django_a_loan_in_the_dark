from django.urls import path
from . import views
from accounts.views import (
    CreateUserView, 
    RedirectDashboardView, 
    CustomLoginView, 
    FirstLoginView, 
    CustomLogoutView, 
    UserDashboardView,
    AdvisorDashboardView,
    UserListView,
    UserEditProfileView,
    UserView
    )

app_name = 'accounts' 

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('first_login/', FirstLoginView.as_view(), name='first_login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', RedirectDashboardView.as_view(), name='dashboard'),
    path('advisor/dashboard/', AdvisorDashboardView.as_view(), name='advisor_dashboard'),
    path('user/dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('user/edit/<uuid:pk>/', UserEditProfileView.as_view(), name='user_edit'),
    path('user/<uuid:pk>/', UserView.as_view(), name='profil'),
    path('advisor/create_user/', CreateUserView.as_view(), name='create_user'),
    path('advisor/list_user/', UserListView.as_view(), name='list_users'),
]

#     path('dashboard/', views.dashboard_view, name='user_dashboard'),
