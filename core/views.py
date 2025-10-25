from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    return render(request, 'core/login.html')

def registro(request):
    return render(request, 'core/registro.html')
