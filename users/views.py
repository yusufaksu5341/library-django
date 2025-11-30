from django.shortcuts import render

def home(request):
    return render(request, 'users/login.html',)

def signup(request):
    return render(request, 'users/signup.html',)