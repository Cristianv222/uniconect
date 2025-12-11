"""
Formularios para el módulo de posts
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, PostImage, PostVideo, PostReport


class PostForm(forms.ModelForm):
    """
    Formulario para crear/editar publicaciones
    """
    
    class Meta:
        model = Post
        fields = ['content', 'privacy', 'location', 'feeling']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '¿Qué estás pensando?',
                'maxlength': 5000
            }),
            'privacy': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Agrega una ubicación...'
            }),
            'feeling': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'content': _('¿Qué estás pensando?'),
            'privacy': _('Privacidad'),
            'location': _('Ubicación'),
            'feeling': _('Sentimiento')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feeling'].required = False
        self.fields['feeling'].widget.choices = [('', 'Sin sentimiento')] + list(self.fields['feeling'].choices)[1:]
        self.fields['location'].required = False


class PostImageForm(forms.ModelForm):
    """
    Formulario para agregar UNA imagen a un post
    """
    
    class Meta:
        model = PostImage
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la imagen (opcional)',
                'maxlength': 200
            })
        }
        labels = {
            'image': _('Imagen'),
            'caption': _('Descripción')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].required = False
        # Agregar clase al widget de imagen
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })


class PostVideoForm(forms.ModelForm):
    """
    Formulario para agregar UN video a un post
    """
    
    class Meta:
        model = PostVideo
        fields = ['video', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del video (opcional)',
                'maxlength': 200
            })
        }
        labels = {
            'video': _('Video'),
            'caption': _('Descripción')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].required = False
        # Agregar clase al widget de video
        self.fields['video'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'video/*'
        })


class PostReportForm(forms.ModelForm):
    """
    Formulario para reportar publicaciones
    """
    
    class Meta:
        model = PostReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el problema con más detalle (opcional)',
                'maxlength': 500
            })
        }
        labels = {
            'reason': _('Razón del reporte'),
            'description': _('Detalles adicionales')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False


class PostShareForm(forms.Form):
    """
    Formulario para compartir un post
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Agrega un comentario (opcional)',
            'maxlength': 5000
        }),
        label=_('¿Qué piensas sobre esto?'),
        required=False
    )
    
    privacy = forms.ChoiceField(
        choices=Post.PRIVACY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Privacidad'),
        initial='friends'
    )


class PostEditForm(forms.ModelForm):
    """
    Formulario para editar solo el contenido y privacidad
    """
    
    class Meta:
        model = Post
        fields = ['content', 'privacy', 'location', 'feeling']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 5000
            }),
            'privacy': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Agrega una ubicación...'
            }),
            'feeling': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'content': _('Contenido'),
            'privacy': _('Privacidad'),
            'location': _('Ubicación'),
            'feeling': _('Sentimiento')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feeling'].required = False
        self.fields['feeling'].widget.choices = [('', 'Sin sentimiento')] + list(self.fields['feeling'].choices)[1:]
        self.fields['location'].required = False


class PostSearchForm(forms.Form):
    """
    Formulario para buscar publicaciones
    """
    query = forms.CharField(
        label=_('Buscar'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar publicaciones...',
            'autocomplete': 'off'
        })
    )
    
    privacy = forms.ChoiceField(
        label=_('Privacidad'),
        required=False,
        choices=[('', 'Todas')] + Post.PRIVACY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    has_media = forms.ChoiceField(
        label=_('Media'),
        required=False,
        choices=[
            ('', 'Todos'),
            ('images', 'Con imágenes'),
            ('videos', 'Con videos'),
            ('media', 'Con imágenes o videos'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        label=_('Desde'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label=_('Hasta'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )