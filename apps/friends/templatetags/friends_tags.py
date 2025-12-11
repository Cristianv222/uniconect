"""
Template tags personalizados para el módulo de friends
"""
from django import template
from apps.friends.models import get_mutual_friends_count, are_friends, has_pending_request

register = template.Library()


@register.filter
def get_mutual_friends_count(user1, user2):
    """
    Obtiene el número de amigos en común entre dos usuarios
    Uso: {{ friend|get_mutual_friends_count:user }}
    """
    try:
        from apps.friends.models import get_mutual_friends_count as get_count
        return get_count(user1, user2)
    except:
        return 0


@register.filter
def are_friends_filter(user1, user2):
    """
    Verifica si dos usuarios son amigos
    Uso: {{ friend|are_friends_filter:user }}
    """
    try:
        return are_friends(user1, user2)
    except:
        return False


@register.filter
def has_pending_request_filter(from_user, to_user):
    """
    Verifica si existe una solicitud pendiente
    Uso: {{ user|has_pending_request_filter:other_user }}
    """
    try:
        return has_pending_request(from_user, to_user)
    except:
        return False