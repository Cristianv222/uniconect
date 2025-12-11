"""
Vistas para el módulo de friends
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils.translation import gettext as _

from apps.authentication.models import User
from .models import (
    Friendship, FriendRequest, BlockedUser, FriendSuggestion,
    are_friends, get_friends, get_friends_count, remove_friendship,
    is_blocked, has_pending_request, get_mutual_friends_count
)
from .forms import FriendRequestForm, BlockUserForm, FriendSearchForm


@login_required
def friends_list(request):
    """
    Lista de amigos del usuario actual
    """
    friends = get_friends(request.user)
    
    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        friends = [
            friend for friend in friends
            if query.lower() in friend.username.lower() or
               query.lower() in friend.get_full_name().lower()
        ]
    
    # Paginación
    paginator = Paginator(friends, 20)
    page_number = request.GET.get('page')
    friends_page = paginator.get_page(page_number)
    
    context = {
        'friends': friends_page,
        'friends_count': len(friends),
        'query': query,
    }
    return render(request, 'friends/friends_list.html', context)


@login_required
def friend_requests(request):
    """
    Lista de solicitudes de amistad (recibidas y enviadas)
    """
    # Solicitudes recibidas (pendientes)
    received_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user', 'from_user__profile').order_by('-created_at')
    
    # Solicitudes enviadas (pendientes)
    sent_requests = FriendRequest.objects.filter(
        from_user=request.user,
        status='pending'
    ).select_related('to_user', 'to_user__profile').order_by('-created_at')
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    return render(request, 'friends/friend_requests.html', context)


@login_required
def send_friend_request(request, username):
    """
    Enviar solicitud de amistad
    """
    to_user = get_object_or_404(User, username=username)
    
    # Validaciones
    if to_user == request.user:
        messages.error(request, _('No puedes enviarte una solicitud a ti mismo.'))
        return redirect('profiles:profile', username=username)
    
    if are_friends(request.user, to_user):
        messages.info(request, _('Ya son amigos.'))
        return redirect('profiles:profile', username=username)
    
    if is_blocked(to_user, request.user):
        messages.error(request, _('No puedes enviar una solicitud a este usuario.'))
        return redirect('profiles:profile', username=username)
    
    if has_pending_request(request.user, to_user):
        messages.info(request, _('Ya enviaste una solicitud a este usuario.'))
        return redirect('profiles:profile', username=username)
    
    # Verificar si hay una solicitud pendiente inversa
    reverse_request = FriendRequest.objects.filter(
        from_user=to_user,
        to_user=request.user,
        status='pending'
    ).first()
    
    if reverse_request:
        # Si existe solicitud inversa, aceptarla directamente
        reverse_request.accept()
        messages.success(request, _('¡Ahora son amigos!'))
        return redirect('profiles:profile', username=username)
    
    # Crear solicitud
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        
        # Crear la solicitud directamente sin usar el formulario
        try:
            friend_request = FriendRequest.objects.create(
                from_user=request.user,
                to_user=to_user,
                message=message
            )
            
            messages.success(request, _('Solicitud de amistad enviada.'))
            return redirect('profiles:profile', username=username)
        except Exception as e:
            messages.error(request, _('Error al enviar la solicitud. Por favor intenta de nuevo.'))
            return redirect('profiles:profile', username=username)
    else:
        form = FriendRequestForm()
    
    context = {
        'form': form,
        'to_user': to_user,
    }
    return render(request, 'friends/send_request.html', context)


@login_required
@require_POST
def accept_friend_request(request, request_id):
    """
    Aceptar solicitud de amistad
    """
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user,
        status='pending'
    )
    
    try:
        friend_request.accept()
        messages.success(request, _('Solicitud aceptada. ¡Ahora son amigos!'))
    except Exception as e:
        messages.error(request, _('Error al aceptar la solicitud.'))
    
    return redirect('friends:friend_requests')


@login_required
@require_POST
def reject_friend_request(request, request_id):
    """
    Rechazar solicitud de amistad
    """
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user,
        status='pending'
    )
    
    try:
        friend_request.reject()
        messages.success(request, _('Solicitud rechazada.'))
    except Exception as e:
        messages.error(request, _('Error al rechazar la solicitud.'))
    
    return redirect('friends:friend_requests')


@login_required
@require_POST
def cancel_friend_request(request, request_id):
    """
    Cancelar solicitud de amistad enviada
    """
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        from_user=request.user,
        status='pending'
    )
    
    try:
        friend_request.cancel()
        messages.success(request, _('Solicitud cancelada.'))
    except Exception as e:
        messages.error(request, _('Error al cancelar la solicitud.'))
    
    return redirect('friends:friend_requests')


@login_required
@require_POST
def remove_friend(request, username):
    """
    Eliminar amistad
    """
    friend = get_object_or_404(User, username=username)
    
    if not are_friends(request.user, friend):
        messages.error(request, _('No son amigos.'))
        return redirect('profiles:profile_detail', username=username)
    
    if remove_friendship(request.user, friend):
        messages.success(request, _('Amistad eliminada.'))
    else:
        messages.error(request, _('Error al eliminar la amistad.'))
    
    return redirect('friends:friends_list')


@login_required
def block_user(request, username):
    """
    Bloquear usuario
    """
    user_to_block = get_object_or_404(User, username=username)
    
    if user_to_block == request.user:
        messages.error(request, _('No puedes bloquearte a ti mismo.'))
        return redirect('profiles:profile_detail', username=username)
    
    if is_blocked(request.user, user_to_block):
        messages.info(request, _('Ya has bloqueado a este usuario.'))
        return redirect('profiles:profile_detail', username=username)
    
    if request.method == 'POST':
        form = BlockUserForm(request.POST)
        if form.is_valid():
            block = form.save(commit=False)
            block.blocker = request.user
            block.blocked = user_to_block
            block.save()
            
            messages.success(request, _('Usuario bloqueado.'))
            return redirect('friends:blocked_users')
    else:
        form = BlockUserForm()
    
    context = {
        'form': form,
        'user_to_block': user_to_block,
    }
    return render(request, 'friends/block_user.html', context)


@login_required
@require_POST
def unblock_user(request, username):
    """
    Desbloquear usuario
    """
    blocked_user = get_object_or_404(User, username=username)
    
    BlockedUser.objects.filter(
        blocker=request.user,
        blocked=blocked_user
    ).delete()
    
    messages.success(request, _('Usuario desbloqueado.'))
    return redirect('friends:blocked_users')


@login_required
def blocked_users_list(request):
    """
    Lista de usuarios bloqueados
    """
    blocked_users = BlockedUser.objects.filter(
        blocker=request.user
    ).select_related('blocked', 'blocked__profile').order_by('-blocked_at')
    
    context = {
        'blocked_users': blocked_users,
    }
    return render(request, 'friends/blocked_users.html', context)


@login_required
def friend_suggestions(request):
    """
    Sugerencias de amistad
    """
    # Obtener sugerencias no descartadas
    suggestions = FriendSuggestion.objects.filter(
        user=request.user,
        is_dismissed=False
    ).select_related('suggested_user', 'suggested_user__profile').order_by('-score', '-created_at')[:20]
    
    # Si no hay sugerencias, generar algunas
    if not suggestions:
        generate_friend_suggestions(request.user)
        suggestions = FriendSuggestion.objects.filter(
            user=request.user,
            is_dismissed=False
        ).select_related('suggested_user', 'suggested_user__profile').order_by('-score', '-created_at')[:20]
    
    context = {
        'suggestions': suggestions,
    }
    return render(request, 'friends/suggestions.html', context)


@login_required
@require_POST
def dismiss_suggestion(request, suggestion_id):
    """
    Descartar sugerencia de amistad
    """
    suggestion = get_object_or_404(
        FriendSuggestion,
        id=suggestion_id,
        user=request.user
    )
    
    suggestion.dismiss()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    messages.success(request, _('Sugerencia descartada.'))
    return redirect('friends:friend_suggestions')


@login_required
def find_friends(request):
    """
    Buscar nuevos amigos
    """
    form = FriendSearchForm(request.GET)
    users = User.objects.none()
    
    if form.is_valid():
        query = form.cleaned_data.get('query', '').strip()
        filter_by = form.cleaned_data.get('filter_by', '')
        
        # Excluir usuarios bloqueados y el usuario actual
        blocked_ids = BlockedUser.objects.filter(
            Q(blocker=request.user) | Q(blocked=request.user)
        ).values_list('blocked_id', 'blocker_id')
        
        blocked_user_ids = set()
        for blocked_id, blocker_id in blocked_ids:
            blocked_user_ids.add(blocked_id)
            blocked_user_ids.add(blocker_id)
        blocked_user_ids.discard(request.user.id)
        
        # Excluir amigos actuales
        current_friends_ids = [friend.id for friend in get_friends(request.user)]
        
        # Query base
        users = User.objects.filter(
            is_active=True
        ).exclude(
            id=request.user.id
        ).exclude(
            id__in=blocked_user_ids
        ).exclude(
            id__in=current_friends_ids
        ).select_related('profile')
        
        # Búsqueda por texto
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        
        # Filtros adicionales
        if filter_by == 'career' and request.user.career:
            users = users.filter(career=request.user.career)
        elif filter_by == 'semester' and request.user.semester:
            users = users.filter(semester=request.user.semester)
        elif filter_by == 'mutual_friends':
            # Usuarios con amigos en común
            my_friends_ids = current_friends_ids
            users = users.filter(
                Q(friendships_as_user1__user2_id__in=my_friends_ids) |
                Q(friendships_as_user2__user1_id__in=my_friends_ids)
            ).distinct()
        
        # Anotar con información adicional
        users = users.annotate(
            has_pending_request=Count(
                Case(
                    When(
                        Q(friend_requests_received__from_user=request.user, 
                          friend_requests_received__status='pending') |
                        Q(friend_requests_sent__to_user=request.user, 
                          friend_requests_sent__status='pending'),
                        then=1
                    ),
                    output_field=IntegerField()
                )
            )
        ).order_by('-has_pending_request', '-date_joined')[:50]
    
    # Paginación
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'users': users_page,
    }
    return render(request, 'friends/find_friends.html', context)


@login_required
def mutual_friends(request, username):
    """
    Ver amigos en común con otro usuario
    """
    other_user = get_object_or_404(User, username=username)
    
    if other_user == request.user:
        messages.error(request, _('No puedes ver esto.'))
        return redirect('friends:friends_list')
    
    from .models import get_mutual_friends
    mutual_friends_list = get_mutual_friends(request.user, other_user)
    
    context = {
        'other_user': other_user,
        'mutual_friends': mutual_friends_list,
        'count': len(mutual_friends_list),
    }
    return render(request, 'friends/mutual_friends.html', context)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def generate_friend_suggestions(user, limit=20):
    """
    Genera sugerencias de amistad para un usuario
    """
    from django.db.models import Count, Q
    
    # Obtener amigos actuales y usuarios bloqueados
    current_friends_ids = [friend.id for friend in get_friends(user)]
    blocked_ids = BlockedUser.objects.filter(
        Q(blocker=user) | Q(blocked=user)
    ).values_list('blocked_id', 'blocker_id')
    
    blocked_user_ids = set()
    for blocked_id, blocker_id in blocked_ids:
        blocked_user_ids.add(blocked_id)
        blocked_user_ids.add(blocker_id)
    blocked_user_ids.discard(user.id)
    
    # Usuarios candidatos
    candidates = User.objects.filter(
        is_active=True
    ).exclude(
        id=user.id
    ).exclude(
        id__in=current_friends_ids
    ).exclude(
        id__in=blocked_user_ids
    ).exclude(
        friend_suggestions__user=user,
        friend_suggestions__is_dismissed=True
    )
    
    suggestions_to_create = []
    
    # 1. Usuarios con amigos en común
    if current_friends_ids:
        users_with_mutual_friends = candidates.filter(
            Q(friendships_as_user1__user2_id__in=current_friends_ids) |
            Q(friendships_as_user2__user1_id__in=current_friends_ids)
        ).annotate(
            mutual_count=Count('id')
        ).order_by('-mutual_count')[:10]
        
        for candidate in users_with_mutual_friends:
            suggestions_to_create.append(
                FriendSuggestion(
                    user=user,
                    suggested_user=candidate,
                    reason='mutual_friends',
                    score=min(1.0, candidate.mutual_count / 10)
                )
            )
    
    # 2. Misma carrera
    if user.career:
        same_career_users = candidates.filter(
            career=user.career
        ).exclude(
            id__in=[s.suggested_user_id for s in suggestions_to_create]
        )[:5]
        
        for candidate in same_career_users:
            suggestions_to_create.append(
                FriendSuggestion(
                    user=user,
                    suggested_user=candidate,
                    reason='same_career',
                    score=0.7
                )
            )
    
    # 3. Mismo semestre
    if user.semester:
        same_semester_users = candidates.filter(
            semester=user.semester
        ).exclude(
            id__in=[s.suggested_user_id for s in suggestions_to_create]
        )[:5]
        
        for candidate in same_semester_users:
            suggestions_to_create.append(
                FriendSuggestion(
                    user=user,
                    suggested_user=candidate,
                    reason='same_semester',
                    score=0.6
                )
            )
    
    # Crear sugerencias en batch
    if suggestions_to_create:
        FriendSuggestion.objects.bulk_create(
            suggestions_to_create[:limit],
            ignore_conflicts=True
        )