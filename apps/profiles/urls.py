from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.authentication.models import User

app_name = 'profiles'

@login_required
def detail_view(request, username):
    user = User.objects.get(username=username)
    return render(request, 'profiles/detail.html', {'profile_user': user})

@login_required
def edit_view(request):
    return render(request, 'profiles/edit.html', {'user': request.user})

urlpatterns = [
    path('<str:username>/', detail_view, name='detail'),
    path('edit/', edit_view, name='edit'),
]