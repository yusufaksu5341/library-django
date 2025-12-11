
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import LibraryUser, Book, Loan, Penalty, Category
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError, models
from django.db.models import Q


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
    user = LibraryUser.objects.filter(pk=user_id).first()
    if not user:
        request.session.flush()
        messages.info(request, 'Oturum süresi doldu, lütfen tekrar giriş yapın.')
        return redirect('users:login')

    books = Book.objects.all().order_by('title')
    categories = Category.objects.all()
    active_loans = Loan.objects.filter(user=user, status='active').values_list('book_id', flat=True)
    
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    available_only = request.GET.get('available') == '1'
    min_year = request.GET.get('min_year', '').strip()
    max_year = request.GET.get('max_year', '').strip()
    
    if category_filter:
        books = books.filter(category_id=category_filter)
    if available_only:
        unavailable_ids = Loan.objects.filter(status='active').values_list('book_id', flat=True)
        books = books.exclude(id__in=unavailable_ids)

    # Smarter search: ignore 1-char terms; require each term to match title or author
    search_terms = [term for term in search_query.split() if len(term) >= 2]
    if search_terms:
        search_filter = Q()
        for term in search_terms:
            search_filter &= (Q(title__icontains=term) | Q(author__name__icontains=term) | Q(author__icontains=term))
        books = books.filter(search_filter)

    # Year filters if provided
    if min_year.isdigit():
        books = books.filter(published_year__gte=int(min_year))
    if max_year.isdigit():
        books = books.filter(published_year__lte=int(max_year))
    
    return render(request, 'home.html', {
        'user': user,
        'books': books,
        'categories': categories,
        'active_book_ids': list(active_loans),
        'selected_category': category_filter,
        'search_query': search_query,
        'available_only': available_only,
        'min_year': min_year,
        'max_year': max_year,
    })


def borrow_book(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('users:login')
    user = LibraryUser.objects.filter(pk=user_id).first()
    if not user:
        request.session.flush()
        messages.info(request, 'Oturum süresi doldu, lütfen tekrar giriş yapın.')
        return redirect('users:login')

    book = get_object_or_404(Book, pk=book_id)

    active_loan = Loan.objects.filter(book=book, status='active').first()
    if active_loan:
        messages.error(request, 'Bu kitap şu an uygun değil.')
        return redirect('users:home')

    user_active_loan_count = Loan.objects.filter(user=user, status='active').count()
    if user_active_loan_count >= 1:
        messages.error(request, 'Aynı anda sadece 1 kitap ödünç alabilirsiniz. Önce mevcut kitabı iade edin.')
        return redirect('users:my_loans')

    existing_active = Loan.objects.filter(user=user, book=book, status='active').exists()
    if existing_active:
        messages.warning(request, 'Bu kitabı zaten ödünç aldınız.')
        return redirect('users:my_loans')

    due_date = timezone.now() + timedelta(days=14)
    Loan.objects.create(
        user=user,
        book=book,
        due_at=due_date,
        status='active'
    )

    messages.success(request, f"'{book.title}' kitabını ödünç aldınız. İade tarihi: {due_date.strftime('%d.%m.%Y')}")
    return redirect('users:my_loans')


def my_loans_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('users:login')
    user = LibraryUser.objects.filter(pk=user_id).first()
    if not user:
        request.session.flush()
        messages.info(request, 'Oturum süresi doldu, lütfen tekrar giriş yapın.')
        return redirect('users:login')

    loans = Loan.objects.filter(user=user).select_related('book', 'book__author').order_by('-borrowed_at')
    return render(request, 'my_loans.html', {'user': user, 'loans': loans})


def return_book(request, loan_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('users:login')
    user = LibraryUser.objects.filter(pk=user_id).first()
    if not user:
        request.session.flush()
        messages.info(request, 'Oturum süresi doldu, lütfen tekrar giriş yapın.')
        return redirect('users:login')

    loan = get_object_or_404(Loan, pk=loan_id, user=user)
    if loan.status != 'active':
        messages.warning(request, 'Bu ödünç kaydı zaten kapatılmış.')
        return redirect('users:my_loans')

    loan.returned_at = timezone.now()
    loan.status = 'returned'
    loan.save(update_fields=['returned_at', 'status'])

    messages.success(request, f"'{loan.book.title}' iade edildi.")
    return redirect('users:my_loans')


def penalties_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('users:login')
    user = LibraryUser.objects.filter(pk=user_id).first()
    if not user:
        request.session.flush()
        messages.info(request, 'Oturum süresi doldu, lütfen tekrar giriş yapın.')
        return redirect('users:login')

    penalties = Penalty.objects.filter(loan__user=user).select_related('loan', 'loan__book').order_by('-calculated_at')
    total_unpaid = penalties.filter(is_paid=False).aggregate(sum_amount=models.Sum('amount'))['sum_amount'] or 0
    return render(request, 'penalties.html', {
        'user': user,
        'penalties': penalties,
        'total_unpaid': total_unpaid,
    })


def logout_view(request):
    try:
        request.session.flush()
    except Exception:
        pass
    messages.info(request, 'Çıkış yapıldı.')
    return redirect('users:login')


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'book_detail.html', {'book': book})