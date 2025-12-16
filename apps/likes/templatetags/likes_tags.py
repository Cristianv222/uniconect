"""
Template tags para el módulo de likes
"""
from django import template
from apps.likes.models import has_user_liked_post, get_user_reaction

register = template.Library()


@register.filter(name='is_liked_by')
def is_liked_by(post, user):
    """
    Verifica si un usuario ha reaccionado a un post
    Uso: {% if post|is_liked_by:user %}
    """
    if not user or not user.is_authenticated:
        return False
    return has_user_liked_post(user, post)


@register.filter(name='user_reaction')
def user_reaction(post, user):
    """
    Obtiene la reacción del usuario en un post
    Uso: {{ post|user_reaction:user }}
    Retorna: 'like', 'love', 'haha', etc. o None
    """
    if not user or not user.is_authenticated:
        return None
    
    reaction = get_user_reaction(user, post)
    return reaction.reaction_type if reaction else None


@register.simple_tag
def get_like_status(post, user):
    """
    Obtiene el estado de reacción de un post para un usuario
    Retorna un diccionario con reacted, reaction_type y count
    """
    if not user or not user.is_authenticated:
        return {'reacted': False, 'reaction_type': None, 'count': post.likes_count}
    
    reaction = get_user_reaction(user, post)
    
    return {
        'reacted': reaction is not None,
        'reaction_type': reaction.reaction_type if reaction else None,
        'count': post.likes_count
    }