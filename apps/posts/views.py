"""
Vistas para el módulo de posts
CRUD completo de publicaciones con imágenes, videos y funcionalidades sociales
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.authentication.models import User
from .models import (
    Post, PostImage, PostVideo, PostMention,
    Hashtag, PostHashtag, PostReport
)
from .forms import (
    PostForm, PostImageForm, PostVideoForm,
    PostReportForm, PostShareForm, PostEditForm,
    PostSearchForm
)


# ============================================================================
# VISTAS DE LISTADO Y DETALLE
# ============================================================================

@login_required
def post_list(request):
    """
    Lista de publicaciones (feed personal)
    Muestra posts del usuario y sus amigos
    """
    # Obtener posts del usuario y sus amigos
    from apps.friends.models import get_friends
    
    friends = get_friends(request.user)
    friend_ids = [friend.id for friend in friends]
    
    # Posts del usuario + posts de amigos + posts públicos
    posts = Post.objects.filter(
        Q(author=request.user) |
        Q(author_id__in=friend_ids, privacy__in=['public', 'friends']) |
        Q(privacy='public')
    ).select_related(
        'author', 'author__profile', 'shared_post', 'shared_post__author'
    ).prefetch_related(
        'images', 'videos', 'mentions', 'post_hashtags__hashtag'
    ).exclude(
        is_archived=True
    ).distinct().order_by('-is_pinned', '-created_at')
    
    # Búsqueda
    search_form = PostSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        privacy = search_form.cleaned_data.get('privacy')
        has_media = search_form.cleaned_data.get('has_media')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if query:
            posts = posts.filter(
                Q(content__icontains=query) |
                Q(author__username__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query)
            )
        
        if privacy:
            posts = posts.filter(privacy=privacy)
        
        if has_media == 'images':
            posts = posts.filter(has_images=True)
        elif has_media == 'videos':
            posts = posts.filter(has_videos=True)
        elif has_media == 'media':
            posts = posts.filter(Q(has_images=True) | Q(has_videos=True))
        
        if date_from:
            posts = posts.filter(created_at__date__gte=date_from)
        
        if date_to:
            posts = posts.filter(created_at__date__lte=date_to)
    
    # Paginación
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'search_form': search_form,
    }
    return render(request, 'posts/post_list.html', context)


@login_required
def post_detail(request, pk):
    """
    Detalle de una publicación
    """
    post = get_object_or_404(
        Post.objects.select_related(
            'author', 'author__profile', 'shared_post', 'shared_post__author'
        ).prefetch_related(
            'images', 'videos', 'mentions__user', 'post_hashtags__hashtag'
        ),
        pk=pk
    )
    
    # Verificar permisos de visualización
    if not post.can_view(request.user):
        messages.error(request, _('No tienes permiso para ver esta publicación.'))
        return redirect('posts:post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def user_posts(request, username):
    """
    Lista de publicaciones de un usuario específico
    """
    user = get_object_or_404(User, username=username)
    
    # Filtrar según privacidad
    if user == request.user:
        # Ver todos sus posts
        posts = Post.objects.filter(author=user)
    else:
        from apps.friends.models import are_friends
        
        if are_friends(request.user, user):
            # Ver posts públicos y de amigos
            posts = Post.objects.filter(
                author=user,
                privacy__in=['public', 'friends']
            )
        else:
            # Solo posts públicos
            posts = Post.objects.filter(
                author=user,
                privacy='public'
            )
    
    posts = posts.select_related(
        'author', 'author__profile', 'shared_post'
    ).prefetch_related(
        'images', 'videos'
    ).exclude(
        is_archived=True
    ).order_by('-is_pinned', '-created_at')
    
    # Paginación
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'posts': page_obj,
    }
    return render(request, 'posts/user_posts.html', context)


# ============================================================================
# VISTAS DE CREACIÓN Y EDICIÓN
# ============================================================================

@login_required
def post_create(request):
    """
    Crear una nueva publicación
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Procesar imágenes
            images = request.FILES.getlist('images')
            for idx, image in enumerate(images):
                PostImage.objects.create(
                    post=post,
                    image=image,
                    order=idx
                )
            
            # Procesar videos
            videos = request.FILES.getlist('videos')
            for idx, video in enumerate(videos):
                PostVideo.objects.create(
                    post=post,
                    video=video,
                    order=idx
                )
            
            # Si es AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'post_id': post.pk,
                    'message': 'Publicación creada exitosamente'
                })
            
            # Si no es AJAX, redirigir al feed
            messages.success(request, _('Publicación creada exitosamente.'))
            return redirect('feed:home')
        else:
            # Si hay errores en el formulario
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Por favor completa el formulario correctamente',
                    'errors': form.errors
                }, status=400)
    else:
        form = PostForm()
    
    context = {
        'form': form,
    }
    return render(request, 'posts/post_create.html', context)

@login_required
def post_edit(request, pk):
    """
    Editar una publicación existente
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Verificar permisos
    if not post.can_edit(request.user):
        messages.error(request, _('No tienes permiso para editar esta publicación.'))
        return redirect('posts:post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)
        
        if form.is_valid():
            post = form.save()
            
            messages.success(request, _('Publicación actualizada exitosamente.'))
            return redirect('posts:post_detail', pk=post.pk)
    else:
        form = PostEditForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'posts/post_edit.html', context)


@login_required
def post_delete(request, pk):
    """
    Eliminar una publicación
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Verificar permisos
    if not post.can_delete(request.user):
        messages.error(request, _('No tienes permiso para eliminar esta publicación.'))
        return redirect('posts:post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('Publicación eliminada exitosamente.'))
        return redirect('posts:post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'posts/post_delete.html', context)


# ============================================================================
# VISTAS DE COMPARTIR
# ============================================================================

@login_required
def post_share(request, pk):
    """
    Compartir una publicación
    """
    original_post = get_object_or_404(Post, pk=pk)
    
    # Verificar que puede ver el post
    if not original_post.can_view(request.user):
        messages.error(request, _('No puedes compartir esta publicación.'))
        return redirect('posts:post_list')
    
    if request.method == 'POST':
        form = PostShareForm(request.POST)
        
        if form.is_valid():
            # Crear nuevo post que comparte el original
            shared_post = Post.objects.create(
                author=request.user,
                content=form.cleaned_data['content'] or '',
                privacy=form.cleaned_data['privacy'],
                shared_post=original_post
            )
            
            # Incrementar contador
            original_post.shares_count += 1
            original_post.save(update_fields=['shares_count'])
            
            messages.success(request, _('Publicación compartida exitosamente.'))
            return redirect('posts:post_detail', pk=shared_post.pk)
    else:
        form = PostShareForm()
    
    context = {
        'form': form,
        'original_post': original_post,
    }
    return render(request, 'posts/post_share.html', context)


# ============================================================================
# VISTAS DE ACCIONES
# ============================================================================

@login_required
def post_pin(request, pk):
    """
    Fijar/Desfijar una publicación
    """
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    post.is_pinned = not post.is_pinned
    post.save(update_fields=['is_pinned'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_pinned': post.is_pinned
        })
    
    action = 'fijada' if post.is_pinned else 'desfijada'
    messages.success(request, _(f'Publicación {action} exitosamente.'))
    return redirect('posts:post_detail', pk=pk)


@login_required
def post_archive(request, pk):
    """
    Archivar/Desarchivar una publicación
    """
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    post.is_archived = not post.is_archived
    post.save(update_fields=['is_archived'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_archived': post.is_archived
        })
    
    action = 'archivada' if post.is_archived else 'desarchivada'
    messages.success(request, _(f'Publicación {action} exitosamente.'))
    
    if post.is_archived:
        return redirect('posts:post_list')
    return redirect('posts:post_detail', pk=pk)


# ============================================================================
# VISTAS DE REPORTES
# ============================================================================

@login_required
def post_report(request, pk):
    """
    Reportar una publicación
    """
    post = get_object_or_404(Post, pk=pk)
    
    # No se puede reportar propio post
    if post.author == request.user:
        messages.error(request, _('No puedes reportar tu propia publicación.'))
        return redirect('posts:post_detail', pk=pk)
    
    # Verificar si ya reportó
    if PostReport.objects.filter(post=post, reporter=request.user).exists():
        messages.info(request, _('Ya has reportado esta publicación.'))
        return redirect('posts:post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostReportForm(request.POST)
        
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            
            messages.success(request, _('Reporte enviado. Lo revisaremos pronto.'))
            return redirect('posts:post_detail', pk=pk)
    else:
        form = PostReportForm()
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'posts/post_report.html', context)


# ============================================================================
# VISTAS DE HASHTAGS
# ============================================================================

@login_required
def hashtag_posts(request, hashtag_name):
    """
    Lista de publicaciones con un hashtag específico
    """
    hashtag = get_object_or_404(Hashtag, name=hashtag_name.lower())
    
    # Obtener posts con este hashtag que el usuario puede ver
    from apps.friends.models import get_friends
    
    friends = get_friends(request.user)
    friend_ids = [friend.id for friend in friends]
    
    posts = Post.objects.filter(
        post_hashtags__hashtag=hashtag
    ).filter(
        Q(author=request.user) |
        Q(author_id__in=friend_ids, privacy__in=['public', 'friends']) |
        Q(privacy='public')
    ).select_related(
        'author', 'author__profile'
    ).prefetch_related(
        'images', 'videos'
    ).exclude(
        is_archived=True
    ).distinct().order_by('-created_at')
    
    # Paginación
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hashtag': hashtag,
        'posts': page_obj,
    }
    return render(request, 'posts/hashtag_posts.html', context)


@login_required
def trending_hashtags(request):
    """
    Lista de hashtags en tendencia
    """
    hashtags = Hashtag.objects.filter(
        posts_count__gt=0
    ).order_by('-posts_count', '-last_used')[:20]
    
    context = {
        'hashtags': hashtags,
    }
    return render(request, 'posts/trending_hashtags.html', context)


# ============================================================================
# VISTAS DE MENCIONES
# ============================================================================

@login_required
def my_mentions(request):
    """
    Posts donde el usuario ha sido mencionado
    """
    mentions = PostMention.objects.filter(
        user=request.user
    ).select_related(
        'post', 'post__author', 'post__author__profile'
    ).prefetch_related(
        'post__images', 'post__videos'
    ).order_by('-created_at')
    
    # Filtrar posts que el usuario puede ver
    posts = []
    for mention in mentions:
        if mention.post.can_view(request.user):
            posts.append(mention.post)
    
    # Paginación
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
    }
    return render(request, 'posts/my_mentions.html', context)


# ============================================================================
# VISTAS DE MEDIA
# ============================================================================

@login_required
def post_add_images(request, pk):
    """
    Agregar imágenes a un post existente
    """
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, _('No tienes permiso para editar esta publicación.'))
        return redirect('posts:post_detail', pk=pk)
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        
        if images:
            current_count = post.images.count()
            for idx, image in enumerate(images):
                PostImage.objects.create(
                    post=post,
                    image=image,
                    order=current_count + idx
                )
            
            messages.success(request, _(f'{len(images)} imagen(es) agregada(s) exitosamente.'))
        else:
            messages.error(request, _('No se seleccionaron imágenes.'))
        
        return redirect('posts:post_detail', pk=pk)
    
    context = {
        'post': post,
    }
    return render(request, 'posts/post_add_images.html', context)


@login_required
def post_delete_image(request, pk):
    """
    Eliminar una imagen de un post
    """
    image = get_object_or_404(PostImage, pk=pk)
    post = image.post
    
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method == 'POST':
        image.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, _('Imagen eliminada exitosamente.'))
        return redirect('posts:post_detail', pk=post.pk)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def post_delete_video(request, pk):
    """
    Eliminar un video de un post
    """
    video = get_object_or_404(PostVideo, pk=pk)
    post = video.post
    
    if post.author != request.user:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method == 'POST':
        video.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, _('Video eliminado exitosamente.'))
        return redirect('posts:post_detail', pk=post.pk)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)