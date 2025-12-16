"""
Vistas para el módulo de likes
Gestión de me gusta en publicaciones
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch

from apps.posts.models import Post
from apps.authentication.models import User
from .models import (
    Like, has_user_liked_post, get_post_likes_count,
    get_post_likers, get_user_liked_posts, toggle_reaction,  # ← Cambiar a toggle_reaction
    remove_like, get_post_reactions_summary, get_user_reaction  # ← Agregar estas dos también
)


# ============================================================================
# VISTAS DE ACCIÓN (AJAX)
# ============================================================================

@login_required
@require_POST
def toggle_like_view(request, post_id):
    """
    Alterna o cambia la reacción en un post
    POST /likes/toggle/<post_id>/
    Body: {"reaction_type": "like"} (opcional, default: "like")
    """
    import json
    
    post = get_object_or_404(
        Post.objects.select_related('author'),
        pk=post_id
    )
    
    # Verificar que puede ver el post
    if not post.can_view(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para ver esta publicación'
            }, status=403)
        
        messages.error(request, _('No tienes permiso para ver esta publicación.'))
        return redirect('posts:post_list')
    
    # Verificar que no está archivado
    if post.is_archived:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No se puede reaccionar a publicaciones archivadas'
            }, status=400)
        
        messages.error(request, _('No se puede reaccionar a publicaciones archivadas.'))
        return redirect('posts:post_detail', pk=post_id)
    
    # Obtener tipo de reacción del body (JSON o form data)
    reaction_type = 'like'  # default
    
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            reaction_type = data.get('reaction_type', 'like')
        except:
            pass
    else:
        reaction_type = request.POST.get('reaction_type', 'like')
    
    # Validar que el tipo de reacción es válido
    valid_reactions = ['like', 'love', 'haha', 'wow', 'sad', 'angry']
    if reaction_type not in valid_reactions:
        reaction_type = 'like'
    
    try:
        reacted, current_reaction, reactions_count = toggle_reaction(request.user, post, reaction_type)
        
        # Obtener resumen de reacciones
        reactions_summary = get_post_reactions_summary(post)
        
        # Respuesta AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Emojis para mostrar
            reaction_emojis = {
                'like': '👍',
                'love': '❤️',
                'haha': '😂',
                'wow': '😮',
                'sad': '😢',
                'angry': '😠',
            }
            
            return JsonResponse({
                'success': True,
                'reacted': reacted,
                'reaction_type': current_reaction,
                'reaction_emoji': reaction_emojis.get(current_reaction, '👍') if current_reaction else None,
                'reactions_count': reactions_count,
                'reactions_summary': reactions_summary,
                'message': f'Reaccionaste con {reaction_emojis.get(current_reaction, "👍")}' if reacted else 'Reacción eliminada'
            })
        
        # Respuesta normal
        if reacted:
            messages.success(request, _('Reacción agregada.'))
        else:
            messages.info(request, _('Reacción eliminada.'))
        
        return redirect('posts:post_detail', pk=post_id)
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        messages.error(request, _('Error al procesar la reacción.'))
        return redirect('posts:post_detail', pk=post_id)

@login_required
@require_POST
def remove_like_view(request, post_id):
    """
    Elimina el like de un post
    POST /likes/remove/<post_id>/
    """
    post = get_object_or_404(Post, pk=post_id)
    
    removed = remove_like(request.user, post)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': removed,
            'likes_count': post.likes_count
        })
    
    if removed:
        messages.success(request, _('Like eliminado.'))
    else:
        messages.info(request, _('No habías dado like a esta publicación.'))
    
    return redirect('posts:post_detail', pk=post_id)


# ============================================================================
# VISTAS DE LISTADO
# ============================================================================

@login_required
def post_likes_list(request, post_id):
    """
    Lista de usuarios que dieron like a un post
    GET /likes/post/<post_id>/
    """
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile'),
        pk=post_id
    )
    
    # Verificar permisos
    if not post.can_view(request.user):
        messages.error(request, _('No tienes permiso para ver esta publicación.'))
        return redirect('posts:post_list')
    
    # Obtener likes con información de usuarios
    likes = Like.objects.filter(
        post=post
    ).select_related(
        'user', 'user__profile'
    ).order_by('-created_at')
    
    # Verificar si el usuario actual dio like
    user_liked = has_user_liked_post(request.user, post)
    
    # Paginación
    paginator = Paginator(likes, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'post': post,
        'likes': page_obj,
        'user_liked': user_liked,
        'total_likes': likes.count(),
    }
    return render(request, 'likes/post_likes_list.html', context)


@login_required
def user_liked_posts(request, username=None):
    """
    Posts a los que un usuario ha dado like
    GET /likes/user/<username>/
    """
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Obtener posts con like
    posts = get_user_liked_posts(user)
    
    # Filtrar según privacidad si no es el usuario actual
    if user != request.user:
        from apps.friends.models import are_friends
        
        visible_posts = []
        for post in posts:
            if post.can_view(request.user):
                visible_posts.append(post)
        posts = visible_posts
    
    # Paginación
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'posts': page_obj,
        'is_own_profile': user == request.user,
    }
    return render(request, 'likes/user_liked_posts.html', context)


@login_required
def my_liked_posts(request):
    """
    Posts a los que el usuario actual ha dado like
    GET /likes/my-likes/
    """
    return user_liked_posts(request, username=None)


# ============================================================================
# VISTAS API AUXILIARES
# ============================================================================

@login_required
def check_like_status(request, post_id):
    """
    Verifica si el usuario actual ha dado like a un post
    GET /likes/check/<post_id>/
    """
    post = get_object_or_404(Post, pk=post_id)
    
    liked = has_user_liked_post(request.user, post)
    likes_count = get_post_likes_count(post)
    
    return JsonResponse({
        'liked': liked,
        'likes_count': likes_count
    })


@login_required
def post_likers_preview(request, post_id):
    """
    Vista previa de usuarios que dieron like (primeros 10)
    GET /likes/post/<post_id>/preview/
    """
    post = get_object_or_404(Post, pk=post_id)
    
    if not post.can_view(request.user):
        return JsonResponse({
            'error': 'No tienes permiso'
        }, status=403)
    
    likers = get_post_likers(post, limit=10)
    
    likers_data = [
        {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'profile_url': f'/profiles/{user.username}/',
        }
        for user in likers
    ]
    
    return JsonResponse({
        'likers': likers_data,
        'total_count': post.likes_count,
        'has_more': post.likes_count > 10
    })