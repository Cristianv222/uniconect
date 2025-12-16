"""
URLs para el módulo de likes
"""
from django.urls import path
from . import views

app_name = 'likes'

urlpatterns = [
    # Acciones de like
    path('toggle/<int:post_id>/', views.toggle_like_view, name='toggle_like'),
    path('remove/<int:post_id>/', views.remove_like_view, name='remove_like'),
    
    # Listados
    path('post/<int:post_id>/', views.post_likes_list, name='post_likes_list'),
    path('user/<str:username>/', views.user_liked_posts, name='user_liked_posts'),
    path('my-likes/', views.my_liked_posts, name='my_liked_posts'),
    
    # API auxiliares
    path('check/<int:post_id>/', views.check_like_status, name='check_like_status'),
    path('post/<int:post_id>/preview/', views.post_likers_preview, name='post_likers_preview'),
]