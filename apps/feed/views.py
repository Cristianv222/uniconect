from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index_view(request):
    """
    Vista principal del feed
    """
    # Import aquí para evitar errores circulares
    from apps.posts.models import Post
    
    print("=" * 50)
    print("INICIANDO VISTA FEED")
    print(f"Usuario: {request.user.username}")
    
    try:
        # Consulta simple sin filtros complejos
        posts = Post.objects.all().order_by('-created_at')
        
        print(f"Query ejecutada, total posts: {posts.count()}")
        
        for post in posts:
            print(f"  - Post {post.id}: {post.content[:30]}")
        
    except Exception as e:
        print(f"ERROR al obtener posts: {e}")
        import traceback
        traceback.print_exc()
        posts = []
    
    context = {
        'posts': posts,
        'stats': {
            'friends_count': 0,
            'notifications_count': 0,
        },
        'unread_notifications': [],
    }
    
    print(f"Context creado con {len(posts)} posts")
    print("=" * 50)
    
    return render(request, 'feed/index.html', context)