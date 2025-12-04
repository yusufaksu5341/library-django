
from django.db import models

class LibraryUser(models.Model):
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school_mail = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.school_mail
