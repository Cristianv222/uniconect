"""
Forms para la app de autenticación
"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, UserInterest


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para crear usuarios
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico (@upec.edu.ec)'
        })
    )
    
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    # Campos de contraseña con estilo
    password1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña nueva',
            'autocomplete': 'new-password'
        }),
    )
    
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    
    career = forms.ChoiceField(
        required=False,
        choices=[('', 'Selecciona tu carrera')] + User.CAREER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    semester = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Semestre',
            'min': 1,
            'max': 10
        })
    )
    
    student_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código de estudiante'
        })
    )
    
    user_type = forms.ChoiceField(
        required=True,
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'password1', 'password2', 'career', 'semester',
            'student_id', 'user_type', 'phone'
        ]
        widgets = {
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirmar contraseña'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ya existe un usuario con este nombre de usuario.")
        return username
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id and User.objects.filter(student_id=student_id).exists():
            raise ValidationError("Ya existe un usuario con este código de estudiante.")
        return student_id


class CustomAuthenticationForm(forms.Form):
    """
    Formulario personalizado para iniciar sesión con email
    """
    
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            # Autenticar directamente con el email
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Por favor ingrese un correo electrónico y contraseña correctos.",
                    code='invalid_login',
                )
            
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    "Esta cuenta está inactiva.",
                    code='inactive',
                )

        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache


class UserProfileUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar el perfil del usuario
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'career', 'semester',
            'student_id', 'phone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'career': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Semestre',
                'min': 1,
                'max': 10
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de estudiante'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
        }
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id and User.objects.filter(student_id=student_id).exclude(
            id=self.instance.id
        ).exists():
            raise ValidationError("Ya existe un usuario con este código de estudiante.")
        return student_id


class ChangePasswordForm(forms.Form):
    """
    Formulario para cambiar contraseña
    """
    
    old_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("La contraseña actual es incorrecta.")
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("Las contraseñas nuevas no coinciden.")
        
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    """
    Formulario para solicitar recuperación de contraseña
    """
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No existe un usuario con este email.")
        return email


class PasswordResetConfirmForm(forms.Form):
    """
    Formulario para confirmar recuperación de contraseña
    """
    
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data


class UserInterestForm(forms.ModelForm):
    """
    Formulario para agregar intereses
    """
    
    class Meta:
        model = UserInterest
        fields = ['category', 'name', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Programación, Fútbol, Fotografía'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción opcional',
                'rows': 3
            }),
        }