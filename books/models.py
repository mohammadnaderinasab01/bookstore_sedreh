from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    book_file_url = models.TextField(max_length=1000)
    purchasers = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='books_purchasers')
    price = models.IntegerField()
    is_banned = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title