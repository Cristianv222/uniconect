# apps/profiles/views.py
"""
Vistas para el módulo de perfiles
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import (
    UserProfile, UserSkill, Education, 
    WorkExperience, PrivacySettings, ProfileView
)
from .forms import (
    UserBasicInfoForm, UserProfileForm, UserSkillForm,
    EducationForm, WorkExperienceForm, PrivacySettingsForm
)

User = get_user_model()


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def profile_view(request, username):
    """
    Vista de perfil de usuario
    """
    profile_user = get_object_or_404(User, username=username)
    
    # Obtener o crear perfil extendido
    user_profile, created = UserProfile.objects.get_or_create(user=profile_user)
    
    # Registrar visita al perfil (solo si no es el propio perfil)
    if request.user != profile_user:
        ProfileView.objects.create(
            viewer=request.user,
            viewed_profile=profile_user,
            ip_address=get_client_ip(request)
        )
    
    # Verificar si son amigos (esto lo implementaremos en el módulo de friends)
    # Por ahora, asumimos que todos pueden ver los perfiles públicos
    is_friend = False  # TODO: Implementar lógica de amistad
    is_own_profile = request.user == profile_user
    
    # Obtener datos adicionales
    skills = profile_user.skills.all()
    education = profile_user.education.all()
    work_experience = profile_user.work_experience.all()
    
    # Obtener configuración de privacidad
    privacy_settings, _ = PrivacySettings.objects.get_or_create(user=profile_user)
    
    # Verificar si el usuario puede ver el perfil
    can_view_profile = (
        is_own_profile or
        privacy_settings.profile_visibility == 'public' or
        (privacy_settings.profile_visibility == 'friends' and is_friend)
    )
    
    if not can_view_profile:
        messages.error(request, 'No tienes permiso para ver este perfil.')
        return redirect('feed:home')  # Redirigir al feed
    
    context = {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'is_own_profile': is_own_profile,
        'is_friend': is_friend,
        'skills': skills,
        'education': education,
        'work_experience': work_experience,
        'privacy_settings': privacy_settings,
    }
    
    return render(request, 'profiles/profile_detail.html', context)


@login_required
def profile_edit(request):
    """
    Editar información del perfil
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        basic_form = UserBasicInfoForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=user_profile
        )
        
        if basic_form.is_valid() and profile_form.is_valid():
            basic_form.save()
            profile_form.save()
            messages.success(request, '¡Perfil actualizado exitosamente!')
            return redirect('profiles:profile', username=request.user.username)
    else:
        basic_form = UserBasicInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'basic_form': basic_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'profiles/profile_edit.html', context)


@login_required
def privacy_settings_view(request):
    """
    Configuración de privacidad
    """
    privacy_settings, created = PrivacySettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=privacy_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de privacidad actualizada.')
            return redirect('profiles:privacy-settings')
    else:
        form = PrivacySettingsForm(instance=privacy_settings)
    
    context = {
        'form': form,
    }
    
    return render(request, 'profiles/privacy_settings.html', context)


# ============================================================================
# SKILLS CRUD
# ============================================================================

@login_required
def skill_add(request):
    """Agregar nueva habilidad"""
    if request.method == 'POST':
        form = UserSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, f'Habilidad "{skill.name}" agregada.')
            return redirect('profiles:profile', username=request.user.username)
    else:
        form = UserSkillForm()
    
    context = {'form': form, 'title': 'Agregar Habilidad'}
    return render(request, 'profiles/skill_form.html', context)


@login_required
def skill_edit(request, pk):
    """Editar habilidad"""
    skill = get_object_or_404(UserSkill, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = UserSkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habilidad actualizada.')
            return redirect('profiles:profile', username=request.user.username)
    else:
        form = UserSkillForm(instance=skill)
    
    context = {'form': form, 'title': 'Editar Habilidad', 'skill': skill}
    return render(request, 'profiles/skill_form.html', context)


@login_required
@require_POST
def skill_delete(request, pk):
    """Eliminar habilidad"""
    skill = get_object_or_404(UserSkill, pk=pk, user=request.user)
    skill_name = skill.name
    skill.delete()
    messages.success(request, f'Habilidad "{skill_name}" eliminada.')
    return redirect('profiles:profile', username=request.user.username)


# ============================================================================
# EDUCATION CRUD
# ============================================================================

@login_required
def education_add(request):
    """Agregar educación"""
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            messages.success(request, 'Educación agregada.')
            return redirect('profiles:profile', username=request.user.username)
    else:
        form = EducationForm()
    
    context = {'form': form, 'title': 'Agregar Educación'}
    return render(request, 'profiles/education_form.html', context)


@login_required
def education_edit(request, pk):
    """Editar educación"""
    education = get_object_or_404(Education, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Educación actualizada.')
            return redirect('profiles:profile', username=request.user.username)
    else:
        form = EducationForm(instance=education)
    
    context = {'form': form, 'title': 'Editar Educación', 'education': education}
    return render(request, 'profiles/education_form.html', context)


@login_required
@require_POST
def education_delete(request, pk):
    """Eliminar educación"""
    education = get_object_or_404(Education, pk=pk, user=request.user)
    education.delete()
    messages.success(request, 'Educación eliminada.')
    return redirect('profiles:profile', username=request.user.username)


# ============================================================================
# WORK EXPERIENCE CRUD
# ============================================================================

@login_required
def work_add(request):
    """Agregar experiencia laboral"""
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            work = form.save(commit=False)
            work.user = request.user
            work.save()
            messages.success(request, 'Experiencia laboral agregada.')
            return redirect('profiles:profile', username=request.user.username)
    else:
        form = WorkExperienceForm()
    
    context = {'form': form, 'title': 'Agregar Experiencia Laboral'}
    return render(request, 'profiles/work_form.html', context)


@login_required
def work_edit(request, pk):
    """Editar experiencia laboral"""
    work = get_object_or_404(WorkExperience, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            messages.success(request, 'Experiencia laboral actualizada.')
            return redirect('profiles:profile', username=request.user.username)
    else:
        form = WorkExperienceForm(instance=work)
    
    context = {'form': form, 'title': 'Editar Experiencia Laboral', 'work': work}
    return render(request, 'profiles/work_form.html', context)


@login_required
@require_POST
def work_delete(request, pk):
    """Eliminar experiencia laboral"""
    work = get_object_or_404(WorkExperience, pk=pk, user=request.user)
    work.delete()
    messages.success(request, 'Experiencia laboral eliminada.')
    return redirect('profiles:profile', username=request.user.username)


# ============================================================================
# BÚSQUEDA DE USUARIOS
# ============================================================================

@login_required
def search_users(request):
    """
    Buscar usuarios
    """
    query = request.GET.get('q', '').strip()
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:20]
    
    context = {
        'query': query,
        'users': users,
    }
    
    return render(request, 'profiles/search_users.html', context)