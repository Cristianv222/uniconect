from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'groups'

@login_required
def list_view(request):
    return render(request, 'groups/list.html')

urlpatterns = [
    path('', list_view, name='list'),
]