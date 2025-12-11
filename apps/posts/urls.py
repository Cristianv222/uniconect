"""
URLs para el módulo de posts
"""
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Listado y detalle
    path('', views.post_list, name='post_list'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('user/<str:username>/', views.user_posts, name='user_posts'),
    
    # Crear, editar, eliminar
    path('create/', views.post_create, name='post_create'),
    path('<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('<int:pk>/delete/', views.post_delete, name='post_delete'),
    
    # Compartir
    path('<int:pk>/share/', views.post_share, name='post_share'),
    
    # Acciones
    path('<int:pk>/pin/', views.post_pin, name='post_pin'),
    path('<int:pk>/archive/', views.post_archive, name='post_archive'),
    
    # Reportes
    path('<int:pk>/report/', views.post_report, name='post_report'),
    
    # Hashtags
    path('hashtag/<str:hashtag_name>/', views.hashtag_posts, name='hashtag_posts'),
    path('hashtags/trending/', views.trending_hashtags, name='trending_hashtags'),
    
    # Menciones
    path('mentions/', views.my_mentions, name='my_mentions'),
    
    # Media
    path('<int:pk>/add-images/', views.post_add_images, name='post_add_images'),
    path('image/<int:pk>/delete/', views.post_delete_image, name='post_delete_image'),
    path('video/<int:pk>/delete/', views.post_delete_video, name='post_delete_video'),
]