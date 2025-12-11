# apps/profiles/forms.py
"""
Formularios para el módulo de perfiles
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import (
    UserProfile, UserSkill, Education, 
    WorkExperience, PrivacySettings
)

User = get_user_model()


class UserBasicInfoForm(forms.ModelForm):
    """
    Formulario para editar información básica del usuario
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'career', 'semester', 'student_id']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+593 XXX XXX XXX'
            }),
            'career': forms.Select(attrs={
                'class': 'form-select'
            }),
            'semester': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Semestre actual',
                'min': 1,
                'max': 10
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de estudiante'
            }),
        }


class UserProfileForm(forms.ModelForm):
    """
    Formulario para editar perfil extendido
    """
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'birth_date', 'gender', 'location', 'website',
            'profile_image', 'cover_image',
            'facebook_url', 'twitter_url', 'instagram_url', 
            'linkedin_url', 'github_url',
            'is_profile_public', 'show_email', 'show_phone'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Cuéntanos sobre ti...',
                'rows': 4,
                'maxlength': 500
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad, País'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://tusitio.com'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/tu-perfil'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/tu-usuario'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/tu-usuario'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/tu-perfil'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/tu-usuario'
            }),
            'is_profile_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_phone': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class UserSkillForm(forms.ModelForm):
    """
    Formulario para agregar habilidades
    """
    class Meta:
        model = UserSkill
        fields = ['name', 'level', 'years_of_experience']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Python, Photoshop, Marketing'
            }),
            'level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Años de experiencia',
                'min': 0,
                'max': 50
            }),
        }


class EducationForm(forms.ModelForm):
    """
    Formulario para agregar educación
    """
    class Meta:
        model = Education
        fields = [
            'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'is_current',
            'grade', 'description'
        ]
        widgets = {
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la institución'
            }),
            'degree': forms.Select(attrs={
                'class': 'form-select'
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Ingeniería de Sistemas'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 9.5/10'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Actividades, logros, proyectos destacados...',
                'rows': 3,
                'maxlength': 500
            }),
        }


class WorkExperienceForm(forms.ModelForm):
    """
    Formulario para agregar experiencia laboral
    """
    class Meta:
        model = WorkExperience
        fields = [
            'company', 'position', 'employment_type',
            'location', 'start_date', 'end_date',
            'is_current', 'description'
        ]
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu cargo'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad, País o Remoto'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Responsabilidades, logros, proyectos destacados...',
                'rows': 4,
                'maxlength': 1000
            }),
        }


class PrivacySettingsForm(forms.ModelForm):
    """
    Formulario para configuración de privacidad
    """
    class Meta:
        model = PrivacySettings
        fields = [
            'profile_visibility', 'email_visibility', 'phone_visibility',
            'birth_date_visibility', 'default_post_privacy',
            'friend_list_visibility', 'who_can_message',
            'email_notifications', 'push_notifications',
            'friend_request_notifications', 'post_like_notifications',
            'comment_notifications', 'mention_notifications'
        ]
        widgets = {
            'profile_visibility': forms.Select(attrs={'class': 'form-select'}),
            'email_visibility': forms.Select(attrs={'class': 'form-select'}),
            'phone_visibility': forms.Select(attrs={'class': 'form-select'}),
            'birth_date_visibility': forms.Select(attrs={'class': 'form-select'}),
            'default_post_privacy': forms.Select(attrs={'class': 'form-select'}),
            'friend_list_visibility': forms.Select(attrs={'class': 'form-select'}),
            'who_can_message': forms.Select(attrs={'class': 'form-select'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'friend_request_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'post_like_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comment_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mention_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }