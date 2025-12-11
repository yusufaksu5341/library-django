from django.contrib import admin
from django import forms
from .models import LibraryUser, Author, Category, Book, Loan, Penalty


@admin.register(LibraryUser)
class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ('school_mail', 'name', 'last_name', 'id', 'get_active_loan')
    search_fields = ('school_mail', 'name', 'last_name')
    list_filter = ('name', 'last_name')
    ordering = ('school_mail',)

    def get_active_loan(self, obj):
        active_loan = Loan.objects.filter(user=obj, status='active').select_related('book').first()
        return active_loan.book.title if active_loan else '-'
    get_active_loan.short_description = 'Aktif Ödünç Kitap'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class BookAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'vLargeTextField richtext-field'}),
        required=False,
        label='Açıklama'
    )

    class Meta:
        model = Book
        fields = '__all__'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    list_display = ('title', 'author', 'get_categories', 'id', 'get_active_borrowers')
    search_fields = ('title', 'author__name', 'categories__name')
    list_filter = ('author', 'categories', 'published_year')
    ordering = ('title',)
    filter_horizontal = ('categories',)

    def get_active_borrowers(self, obj):
        borrowers = Loan.objects.filter(book=obj, status='active').select_related('user').values_list('user__school_mail', flat=True)
        return ', '.join(borrowers) if borrowers else '-'
    get_active_borrowers.short_description = 'Aktif Ödünç Alanlar'

    def get_categories(self, obj):
        names = obj.categories.values_list('name', flat=True)
        return ', '.join(names) if names else '-'
    get_categories.short_description = 'Kategoriler'
    get_categories.admin_order_field = 'categories__name'

    class Media:
        css = {'all': ('users/admin-richtext.css',)}
        js = ('users/admin-richtext.js',)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_at', 'due_at', 'returned_at', 'status')
    search_fields = ('user__school_mail', 'book__title')
    list_filter = ('status', 'borrowed_at')
    readonly_fields = ('borrowed_at',)


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'reason', 'is_paid', 'calculated_at')
    search_fields = ('loan__user__school_mail', 'reason')
    list_filter = ('is_paid', 'calculated_at')
