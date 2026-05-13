from django.shortcuts import render
from tickets.models import Town


def home(request):
    towns = Town.objects.all()
    return render(request, 'landing/home.html', {'towns': towns})
