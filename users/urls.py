
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.login_view, name='login'),         # /  → login.html
    path('signup/', views.signup_view, name='signup') # /signup/ → signup.html
]
