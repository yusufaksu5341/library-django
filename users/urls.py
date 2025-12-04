
# users/urls.py
from django.urls import path
from users.views import signup, login_view, home_view, logout_view

app_name = 'users'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup, name='signup'),
]