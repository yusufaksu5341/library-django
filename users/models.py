
from django.db import models
from datetime import timedelta
from django.utils import timezone


class LibraryUser(models.Model):
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school_mail = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.school_mail


class Author(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    published_year = models.PositiveIntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=20, unique=True)
    available_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.author}"


class Loan(models.Model):
    LOAN_STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('returned', 'İade Edildi'),
        ('overdue', 'Gecikmiş'),
    ]

    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.user} - {self.book.title}"

    def is_overdue(self):
        return not self.returned_at and timezone.now() > self.due_at

    def days_overdue(self):
        if self.is_overdue():
            return (timezone.now() - self.due_at).days
        return 0


class Penalty(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='penalty')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    calculated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Ceza: {self.loan.user} - {self.amount} TL"
