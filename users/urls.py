
# users/urls.py
from django.urls import path
from users.views import (
    signup,
    login_view,
    home_view,
    logout_view,
    borrow_book,
    my_loans_view,
    return_book,
    penalties_view,
)

app_name = 'users'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup, name='signup'),
    path('borrow/<int:book_id>/', borrow_book, name='borrow_book'),
    path('loans/', my_loans_view, name='my_loans'),
    path('return/<int:loan_id>/', return_book, name='return_book'),
    path('penalties/', penalties_view, name='penalties'),
]