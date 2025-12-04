
# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import LibraryUser
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError


def login_view(request):
    if request.method == 'POST':
        school_mail = request.POST.get('schoolMail', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([school_mail, password]):
            messages.error(request, 'Lütfen tüm alanları doldurun.')
            return render(request, 'login.html')

        try:
            user = LibraryUser.objects.get(school_mail=school_mail)
            if check_password(password, user.password):
                # Login başarılı - session'a user bilgisi eklenir
                request.session['user_id'] = user.id
                request.session['user_mail'] = user.school_mail
                messages.success(request, f'Hoş geldin {user.name}!')
                return redirect('users:home')
            else:
                messages.error(request, 'Hatalı şifre!')
        except LibraryUser.DoesNotExist:
            messages.error(request, 'Bu mail ile kayıtlı kullanıcı bulunamadı!')

        return render(request, 'login.html')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        school_mail = request.POST.get('schoolMail', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirmPassword', '').strip()

        if not all([name, last_name, school_mail, password, confirm_password]):
            messages.error(request, 'Lütfen tüm alanları doldurun.')
            return render(request, 'signup.html', {
                'name': name,
                'lastName': last_name,
                'schoolMail': school_mail,
            })

        if password != confirm_password:
            messages.error(request, 'Şifreler eşleşmiyor!')
            return render(request, 'signup.html', {
                'name': name,
                'lastName': last_name,
                'schoolMail': school_mail,
            })

        if not school_mail.endswith('@ktu.edu.tr'):
            messages.error(request, 'Sadece @ktu.edu.tr uzantılı mailler kabul edilir!')
            return render(request, 'signup.html', {
                'name': name,
                'lastName': last_name,
                'schoolMail': school_mail,
            })

        if len(password) < 6:
            messages.error(request, 'Şifre en az 6 karakter olmalı!')
            return render(request, 'signup.html', {
                'name': name,
                'lastName': last_name,
                'schoolMail': school_mail,
            })

        if LibraryUser.objects.filter(school_mail=school_mail).exists():
            messages.error(request, 'Bu mail zaten kayıtlı!')
            return render(request, 'signup.html', {
                'name': name,
                'lastName': last_name,
                'schoolMail': school_mail,
            })

        try:
            LibraryUser.objects.create(
                name=name,
                last_name=last_name,
                school_mail=school_mail,
                password=make_password(password)
            )
        except IntegrityError:
            messages.error(request, 'Kayıt sırasında bir hata oluştu (benzersizlik).')
            return render(request, 'signup.html', {
                'name': name,
                'lastName': last_name,
                'schoolMail': school_mail,
            })

        messages.success(request, 'Kayıt başarılı!')
        try:
            return redirect('users:login')
        except Exception:
            return redirect('login')

    return render(request, 'signup.html')


def home_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('users:login')

    user = get_object_or_404(LibraryUser, pk=user_id)
    return render(request, 'home.html', {'user': user})


def logout_view(request):
    try:
        request.session.flush()
    except Exception:
        pass
    messages.info(request, 'Çıkış yapıldı.')
    return redirect('users:login')
