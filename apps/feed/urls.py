from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'feed'

@login_required
def index_view(request):
    return render(request, 'feed/index.html', {'user': request.user})

urlpatterns = [
    path('', index_view, name='index'),
]