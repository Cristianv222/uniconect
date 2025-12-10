"""
URLs para la app de autenticación
Incluye tanto endpoints de API como vistas de templates
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # =========================================================================
    # VISTAS DE TEMPLATES (para navegador)
    # =========================================================================
    
    # Autenticación con templates
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # =========================================================================
    # API ENDPOINTS (para aplicaciones frontend)
    # =========================================================================
    
    # Autenticación API
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
    
    # Usuario actual API
    path('api/me/', views.CurrentUserView.as_view(), name='api-current-user'),
    
    # Perfil API
    path('api/profile/update/', views.UserProfileUpdateView.as_view(), name='api-profile-update'),
    
    # Cambio de contraseña API
    path('api/password/change/', views.ChangePasswordView.as_view(), name='api-password-change'),
    
    # Recuperación de contraseña API
    path('api/password/reset/request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('api/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Verificación de email (compartido entre template y API)
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    
    # Intereses del usuario API
    path('api/interests/', views.UserInterestListCreateView.as_view(), name='api-interest-list-create'),
    path('api/interests/<int:pk>/', views.UserInterestDetailView.as_view(), name='api-interest-detail'),
    
    # Historial de inicios de sesión API
    path('api/login-history/', views.LoginHistoryListView.as_view(), name='api-login-history'),
]