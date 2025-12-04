from django.contrib import admin
from .models import LibraryUser


@admin.register(LibraryUser)
class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ('school_mail', 'name', 'last_name', 'id', 'password_display')
    search_fields = ('school_mail', 'name', 'last_name')
    list_filter = ('name', 'last_name')
    ordering = ('school_mail',)
    
   
    def password_display(self, obj):
        return obj.password[:50] + '...' if len(obj.password) > 50 else obj.password
    password_display.short_description = 'Şifre (Hash)'
    
    fields = ('name', 'last_name', 'school_mail')
    readonly_fields = []
