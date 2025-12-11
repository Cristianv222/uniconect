"""
Formularios para el módulo de friends
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FriendRequest, BlockedUser


class FriendRequestForm(forms.ModelForm):
    """
    Formulario para enviar solicitud de amistad
    """
    
    class Meta:
        model = FriendRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe un mensaje opcional...',
                'maxlength': 200
            })
        }
        labels = {
            'message': _('Mensaje (opcional)')
        }


class BlockUserForm(forms.ModelForm):
    """
    Formulario para bloquear usuario
    """
    
    class Meta:
        model = BlockedUser
        fields = ['reason']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'reason': _('Razón del bloqueo')
        }


class FriendSearchForm(forms.Form):
    """
    Formulario para buscar amigos
    """
    
    query = forms.CharField(
        label=_('Buscar'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o username...',
            'autocomplete': 'off'
        })
    )
    
    filter_by = forms.ChoiceField(
        label=_('Filtrar por'),
        required=False,
        choices=[
            ('', 'Todos'),
            ('career', 'Misma carrera'),
            ('semester', 'Mismo semestre'),
            ('mutual_friends', 'Amigos en común'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )