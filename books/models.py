from django.core.validators import *
from django.db import models
from django.conf import settings
from django.utils import timezone

class Type(models.Model):
    name = models.CharField(max_length=2500)

    def __str__(self):
       return self.name



class Author(models.Model):
    name = models.CharField(max_length=2500)

    def __str__(self):
       return self.name


class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ForeignKey(Type, related_name='type', on_delete=models.CASCADE)
    description = models.TextField()
    pdf = models.FileField(upload_to='books/', validators=[FileExtensionValidator(['pdf'])], blank=True, null=True)
    cover_image = models.ImageField(upload_to='books/covers/',default=False)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, default=False)
    location = models.TextField(max_length=500, default=False)
    views = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['user_id', 'book_id'], name='unique_user_book')
    #     ]
    def __str__(self):
        return f"{self.book.title} in {self.user.name}'s cart"