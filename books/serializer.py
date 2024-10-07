from rest_framework import serializers
from .models import Book
from utils.bucket_abr_arvan import BooksBucket


class BookCreateOrUpdateOrDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ('id',)

class BookCreateSerializerRequest(serializers.ModelSerializer):
    book_file = serializers.FileField(required=True)
    class Meta:
        model = Book
        exclude = ('id', 'book_file_url', 'purchasers')

class BookUpdateSerializerRequest(serializers.ModelSerializer):
    book_file = serializers.FileField(required=False)
    title = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    class Meta:
        model = Book
        exclude = ('id', 'book_file_url', 'purchasers')

class BookReadSerializer(serializers.ModelSerializer):
    book_file_url = serializers.SerializerMethodField('get_book_file_bucket_url')
    class Meta:
        model = Book
        fields = '__all__'
        depth = 1
    
    def get_book_file_bucket_url(self, object):
        books_bucket = BooksBucket()
        return books_bucket.GetDownloadLink(object.book_file_url)
    
    
class PurchaseBookRequest(serializers.Serializer):
    book_id = serializers.IntegerField(required=True)
    
class PurchaseBookResponse(serializers.Serializer):
    book_file_url = serializers.SerializerMethodField('get_book_file_bucket_url')

    def get_book_file_bucket_url(self, object):
        books_bucket = BooksBucket()
        return books_bucket.GetDownloadLink(object.book_file_url)