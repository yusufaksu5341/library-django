
# users/urls.py
from django.urls import path
from users.views import signup, login_view

app_name = 'users'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
]
