from django.contrib import admin
from .models import Category, Book


admin.site.register(Book)
admin.site.register(Category)