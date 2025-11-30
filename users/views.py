
from django.shortcuts import render

def login_view(request):
    return render(request, 'users/signup.html')

def signup_view(request):
    return render(request, 'users/signup.html')
