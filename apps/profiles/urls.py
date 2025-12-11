# apps/profiles/urls.py
"""
URLs para el módulo de perfiles
"""
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Perfil principal
    path('<str:username>/', views.profile_view, name='profile'),
    path('edit/profile/', views.profile_edit, name='profile-edit'),
    path('settings/privacy/', views.privacy_settings_view, name='privacy-settings'),
    
    # Habilidades (Skills)
    path('skills/add/', views.skill_add, name='skill-add'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='skill-edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill-delete'),
    
    # Educación
    path('education/add/', views.education_add, name='education-add'),
    path('education/<int:pk>/edit/', views.education_edit, name='education-edit'),
    path('education/<int:pk>/delete/', views.education_delete, name='education-delete'),
    
    # Experiencia laboral
    path('work/add/', views.work_add, name='work-add'),
    path('work/<int:pk>/edit/', views.work_edit, name='work-edit'),
    path('work/<int:pk>/delete/', views.work_delete, name='work-delete'),
    
    # Búsqueda
    path('search/users/', views.search_users, name='search-users'),
]