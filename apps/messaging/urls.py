from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'messaging'

@login_required
def inbox_view(request):
    return render(request, 'messaging/inbox.html')

urlpatterns = [
    path('inbox/', inbox_view, name='inbox'),
]