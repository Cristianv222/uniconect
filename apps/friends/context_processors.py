"""
Context processors para el módulo de friends
Proporciona datos de amigos a todos los templates
"""
from .models import FriendRequest


def friends_context(request):
    """
    Añade información de amigos al contexto global
    """
    if request.user.is_authenticated:
        # Contar solicitudes pendientes
        pending_requests_count = FriendRequest.objects.filter(
            to_user=request.user,
            status='pending'
        ).count()
        
        return {
            'pending_friend_requests_count': pending_requests_count,
        }
    
    return {
        'pending_friend_requests_count': 0,
    }