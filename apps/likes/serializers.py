"""
Serializers para el módulo de likes (API DRF)
"""
from rest_framework import serializers
from .models import Like
from apps.authentication.serializers import UserSerializer


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer para likes
    """
    user = UserSerializer(read_only=True)
    post_id = serializers.IntegerField(source='post.id', read_only=True)
    
    class Meta:
        model = Like
        fields = [
            'id',
            'user',
            'post_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class LikeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear likes
    """
    
    class Meta:
        model = Like
        fields = ['post']
    
    def validate_post(self, value):
        """
        Validar que el post existe y puede recibir likes
        """
        if value.is_archived:
            raise serializers.ValidationError(
                "No se puede dar like a publicaciones archivadas."
            )
        
        request = self.context.get('request')
        if request and not value.can_view(request.user):
            raise serializers.ValidationError(
                "No tienes permiso para ver esta publicación."
            )
        
        return value
    
    def create(self, validated_data):
        """
        Crear o retornar like existente
        """
        user = self.context['request'].user
        post = validated_data['post']
        
        like, created = Like.objects.get_or_create(
            user=user,
            post=post
        )
        
        return like


class PostLikesSummarySerializer(serializers.Serializer):
    """
    Serializer para resumen de likes de un post
    """
    likes_count = serializers.IntegerField()
    user_liked = serializers.BooleanField()
    recent_likers = UserSerializer(many=True, read_only=True)