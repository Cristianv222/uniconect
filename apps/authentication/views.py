"""
Views para la app de autenticación
Incluye tanto vistas API (DRF) como vistas para templates HTML
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import secrets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, UserInterest, PasswordResetToken, EmailVerificationToken, LoginHistory
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, UserProfileUpdateSerializer,
    UserInterestSerializer, LoginHistorySerializer
)
from .forms import CustomUserCreationForm, CustomAuthenticationForm


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_client_ip(request):
    """
    Obtener IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_type(request):
    """
    Detectar tipo de dispositivo
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'mobile' in user_agent:
        return 'mobile'
    elif 'tablet' in user_agent:
        return 'tablet'
    else:
        return 'desktop'


# ==============================================================================
# VISTAS PARA TEMPLATES HTML (NAVEGADOR)
# ==============================================================================

@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Vista para registro de usuarios con formulario Django
    """
    # CAMBIO: Redirigir al feed si ya está autenticado
    if request.user.is_authenticated:
        return redirect('feed:home')  # Cambia a feed en lugar de home
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.objects.create(
                user=user,
                token=secrets.token_urlsafe(32),
                expires_at=timezone.now() + timedelta(days=1)
            )
            
            # TODO: Enviar email de verificación
            # send_verification_email(user, verification_token.token)
            
            messages.success(
                request, 
                f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.'
            )
            
            # Iniciar sesión automáticamente
            # IMPORTANTE: Usar authenticate primero
            authenticated_user = authenticate(
                request,
                username=user.email,  # Usamos email como username
                password=form.cleaned_data.get('password1')  # Contraseña en texto plano del formulario
            )
            
            if authenticated_user:
                login(request, authenticated_user)
            
            # CAMBIO: Redirigir al feed después de registro exitoso
            return redirect('feed:home')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'authentication/register.html', {
        'form': form,
        'title': 'Registro - UnicoNet'
    })

@csrf_exempt 
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista para inicio de sesión con formulario Django
    """
    # CAMBIO: Redirigir al feed si ya está autenticado
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me', False)
            
            if user is not None:
                login(request, user)
                
                # Configurar duración de sesión
                if not remember_me:
                    request.session.set_expiry(0)  # Expira al cerrar navegador
                else:
                    request.session.set_expiry(1209600)  # 2 semanas
                
                # Registrar inicio de sesión
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    device_type=get_device_type(request),
                    success=True
                )
                
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
                
                # CAMBIO: Redirigir al feed en lugar de home
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('feed:home')  # Redirigir al feed
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'authentication/login.html', {
        'form': form,
        'title': 'Iniciar Sesión - UnicoNet'
    })


@require_http_methods(["POST", "GET"])
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    if request.user.is_authenticated:
        messages.info(request, f'Hasta pronto, {request.user.first_name}.')
        logout(request)
    return redirect('home')


# ==============================================================================
# API VIEWS (REST FRAMEWORK)
# ==============================================================================

class RegisterView(APIView):
    """
    Vista API para registrar nuevos usuarios
    POST /auth/api/register/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Crear token de autenticación
            token, created = Token.objects.get_or_create(user=user)
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.objects.create(
                user=user,
                token=secrets.token_urlsafe(32),
                expires_at=timezone.now() + timedelta(days=1)
            )
            
            # TODO: Enviar email de verificación
            # send_verification_email(user, verification_token.token)
            
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Vista API para iniciar sesión
    POST /auth/api/login/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Iniciar sesión
            login(request, user)
            
            # Crear o obtener token
            token, created = Token.objects.get_or_create(user=user)
            
            # Registrar inicio de sesión
            LoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                device_type=get_device_type(request),
                success=True
            )
            
            return Response({
                'message': 'Inicio de sesión exitoso',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        
        # Registrar intento fallido si hay email
        email = request.data.get('email')
        if email:
            try:
                user = User.objects.get(email=email.lower())
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    device_type=get_device_type(request),
                    success=False
                )
            except User.DoesNotExist:
                pass
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Vista API para cerrar sesión
    POST /auth/api/logout/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Eliminar token
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        # Cerrar sesión
        logout(request)
        
        return Response({
            'message': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Vista API para obtener información del usuario actual
    GET /auth/api/me/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Vista API para actualizar el perfil del usuario
    PUT/PATCH /auth/api/profile/update/
    """
    
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Vista API para cambiar contraseña
    POST /auth/api/password/change/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Eliminar token actual
            try:
                request.user.auth_token.delete()
            except:
                pass
            
            # Crear nuevo token
            token = Token.objects.create(user=request.user)
            
            return Response({
                'message': 'Contraseña cambiada exitosamente',
                'token': token.key
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Vista API para solicitar recuperación de contraseña
    POST /auth/api/password/reset/request/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Crear token de recuperación
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=secrets.token_urlsafe(32),
                expires_at=timezone.now() + timedelta(hours=1)
            )
            
            # TODO: Enviar email con el token
            # send_password_reset_email(user, reset_token.token)
            
            return Response({
                'message': 'Se ha enviado un email con instrucciones para recuperar tu contraseña'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Vista API para confirmar recuperación de contraseña
    POST /auth/api/password/reset/confirm/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token_str = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token_str)
                
                if not reset_token.is_valid():
                    return Response({
                        'error': 'El token ha expirado o ya fue usado'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Cambiar contraseña
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Marcar token como usado
                reset_token.mark_as_used()
                
                # Eliminar tokens antiguos del usuario
                Token.objects.filter(user=user).delete()
                
                # Crear nuevo token
                token = Token.objects.create(user=user)
                
                return Response({
                    'message': 'Contraseña restablecida exitosamente',
                    'token': token.key
                }, status=status.HTTP_200_OK)
                
            except PasswordResetToken.DoesNotExist:
                return Response({
                    'error': 'Token inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    Vista API para verificar email
    GET /auth/verify-email/<token>/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            
            if not verification_token.is_valid():
                return Response({
                    'error': 'El token ha expirado o ya fue usado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar usuario
            user = verification_token.user
            user.is_verified = True
            user.save()
            
            # Marcar token como usado
            verification_token.mark_as_used()
            
            return Response({
                'message': 'Email verificado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except EmailVerificationToken.DoesNotExist:
            return Response({
                'error': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserInterestListCreateView(generics.ListCreateAPIView):
    """
    Vista API para listar y crear intereses del usuario
    GET/POST /auth/api/interests/
    """
    
    serializer_class = UserInterestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserInterest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserInterestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista API para ver, actualizar y eliminar un interés
    GET/PUT/PATCH/DELETE /auth/api/interests/<id>/
    """
    
    serializer_class = UserInterestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserInterest.objects.filter(user=self.request.user)


class LoginHistoryListView(generics.ListAPIView):
    """
    Vista API para ver el historial de inicios de sesión
    GET /auth/api/login-history/
    """
    
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LoginHistory.objects.filter(
            user=self.request.user
        ).order_by('-login_time')[:20]  # Últimos 20 inicios de sesión