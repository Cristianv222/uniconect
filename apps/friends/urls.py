from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'friends'

@login_required
def list_view(request):
    return render(request, 'friends/list.html')

urlpatterns = [
    path('', list_view, name='list'),
]