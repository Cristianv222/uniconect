"""
URLs para el módulo de friends
"""
from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    # Lista de amigos
    path('', views.friends_list, name='friends_list'),
    
    # Solicitudes de amistad
    path('requests/', views.friend_requests, name='friend_requests'),
    path('send/<str:username>/', views.send_friend_request, name='send_request'),
    path('accept/<int:request_id>/', views.accept_friend_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_friend_request, name='reject_request'),
    path('cancel/<int:request_id>/', views.cancel_friend_request, name='cancel_request'),
    
    # Gestión de amistades
    path('remove/<str:username>/', views.remove_friend, name='remove_friend'),
    path('mutual/<str:username>/', views.mutual_friends, name='mutual_friends'),
    
    # Bloqueos
    path('block/<str:username>/', views.block_user, name='block_user'),
    path('unblock/<str:username>/', views.unblock_user, name='unblock_user'),
    path('blocked/', views.blocked_users_list, name='blocked_users'),
    
    # Sugerencias
    path('suggestions/', views.friend_suggestions, name='friend_suggestions'),
    path('suggestions/dismiss/<int:suggestion_id>/', views.dismiss_suggestion, name='dismiss_suggestion'),
    
    # Búsqueda
    path('find/', views.find_friends, name='find_friends'),
]