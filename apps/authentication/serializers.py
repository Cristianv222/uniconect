"""
Serializers para la app de autenticación
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserInterest, LoginHistory


class UserInterestSerializer(serializers.ModelSerializer):
    """
    Serializer para los intereses del usuario
    """
    
    class Meta:
        model = UserInterest
        fields = ['id', 'category', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User
    """
    
    interests = UserInterestSerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'career', 'semester', 'student_id', 'user_type',
            'phone', 'is_active', 'is_verified', 'date_joined',
            'interests'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    interests = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'career', 'semester',
            'student_id', 'user_type', 'phone', 'interests'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Validar que las contraseñas coincidan
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        return attrs
    
    def validate_email(self, value):
        """
        Validar que el email no exista
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este email."
            )
        return value.lower()
    
    def validate_username(self, value):
        """
        Validar que el username no exista
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este nombre de usuario."
            )
        return value.lower()
    
    def validate_student_id(self, value):
        """
        Validar que el código de estudiante sea único
        """
        if value and User.objects.filter(student_id=value).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este código de estudiante."
            )
        return value
    
    def create(self, validated_data):
        """
        Crear nuevo usuario
        """
        # Remover campos que no van al modelo
        validated_data.pop('password_confirm')
        interests_data = validated_data.pop('interests', [])
        
        # Crear usuario
        user = User.objects.create_user(**validated_data)
        
        # Crear intereses si se proporcionaron
        for interest_data in interests_data:
            UserInterest.objects.create(user=user, **interest_data)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer para el inicio de sesión
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """
        Validar credenciales del usuario
        """
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            # Intentar autenticar
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    "Email o contraseña incorrectos.",
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    "Esta cuenta está desactivada.",
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                "Debe proporcionar email y contraseña.",
                code='authorization'
            )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña
    """
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
        validators=[validate_password]
    )
    
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate_old_password(self, value):
        """
        Validar que la contraseña actual sea correcta
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "La contraseña actual es incorrecta."
            )
        return value
    
    def validate(self, attrs):
        """
        Validar que las contraseñas nuevas coincidan
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Las contraseñas no coinciden."
            })
        return attrs
    
    def save(self, **kwargs):
        """
        Guardar nueva contraseña
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer para solicitar recuperación de contraseña
    """
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """
        Validar que el email exista
        """
        value = value.lower()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No existe un usuario con este email."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para confirmar recuperación de contraseña
    """
    
    token = serializers.CharField(required=True)
    
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True,
        validators=[validate_password]
    )
    
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """
        Validar que las contraseñas coincidan
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Las contraseñas no coinciden."
            })
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar el perfil del usuario
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'career', 'semester',
            'student_id', 'phone'
        ]
    
    def validate_student_id(self, value):
        """
        Validar que el código de estudiante sea único
        """
        user = self.context['request'].user
        if value and User.objects.filter(student_id=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este código de estudiante."
            )
        return value


class LoginHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de inicios de sesión
    """
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'login_time', 'ip_address', 'user_agent',
            'device_type', 'location', 'success'
        ]
        read_only_fields = ['id', 'login_time'] 