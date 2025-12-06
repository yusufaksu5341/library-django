
from django.db import models


class LibraryUser(models.Model):
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school_mail = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.school_mail


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_year = models.PositiveIntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=20, unique=True)
    available_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.author}"
