from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializer import BookCreateOrUpdateOrDeleteSerializer, BookReadSerializer, BookCreateSerializerRequest, BookUpdateSerializerRequest, PurchaseBookRequest, PurchaseBookResponse
from .models import Book, Category
from utils.bucket_abr_arvan import BooksBucket
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_spectacular.utils import extend_schema
from users.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from authentication.authentication import UserAuthentication
from django.conf import settings
from users.models import UserWallet
import os, uuid


user_authentication = UserAuthentication

class PageNumberPagination(pagination.PageNumberPagination):       
    page_size = settings.PAGINATION_PAGE_SIZE

class BooksViewSet(GenericViewSet):
    queryset = Book.objects.all()
    pagination_class = PageNumberPagination
    parser_classes = (MultiPartParser, JSONParser)
    
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.path == '/books/purchase-book/':
            self.args = args
            self.kwargs = kwargs
            request = self.initialize_request(request, *args, **kwargs)
            self.request = request
            self.headers = self.default_response_headers
            self.authentication_classes = [UserAuthentication]

            response_exc = ''
            try:
                self.initial(request, *args, **kwargs)

                # Get the appropriate handler method
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(),
                                    self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed

                response = handler(request, *args, **kwargs)

            except Exception as exc:
                response_exc = exc
                response = self.handle_exception(exc)

            self.response = self.finalize_response(request, response, *args, **kwargs)
            if str(response_exc) == 'Invalid Token':
                self.response.status_code = 401
            return self.response
        self.authentication_classes = []
        return super().dispatch(request, *args, **kwargs)


    def get_serializer_class(self, *args, **kwargs):
        if (self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE') and self.request.path != '/books/purchase-book/':
            return BookCreateOrUpdateOrDeleteSerializer
        elif self.request.method == 'GET':
            return BookReadSerializer

    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated(), IsAdminUser()]

        
    @extend_schema(
        request=BookCreateSerializerRequest
    )
    def create(self, request):
        try:
            updated_data = request.data.dict().copy()
            if updated_data.get('book_file') != None and request.data['book_file'] != '':
                updated_data.pop('book_file')
                books_bucket = BooksBucket()
                name, extension = os.path.splitext(request.FILES.get('book_file').name)
                rnd_filename = f'{uuid.uuid4()}{extension.lower()}'
                books_bucket.UploadFile(src_file_path=request.FILES.get('book_file'), filename=rnd_filename)
                updated_data['book_file_url'] = rnd_filename
            serializer = BookCreateOrUpdateOrDeleteSerializer(data=updated_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                        'validationMessage': [{
                            'statusCode': 201,
                            'message': 'اطلاعات با موفقیت ذخیره شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=201)
        except Exception as e:
            print(e)
            print(type(e))
            return Response({
                        'validationMessage': [{
                            'statusCode': 406,
                            'message': e
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=406)
            

    def list(self, request):
        try:
            # only some of users (in my test case, superusers) can see all the books even banned books, other users can only see unbanned books
            if request.user.is_superuser:
                queryset = Book.objects.all()
            else:
                queryset = Book.objects.filter(is_banned=False)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = BookReadSerializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                response.data['page_size'] = settings.PAGINATION_PAGE_SIZE
                return response
            else:
                return Response({
                    'validationMessage': [{
                        'statusCode': 404,
                        'message': 'اطلاعاتی یافت نشد'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=404)
        except Exception as e:
            print('error: %s' % e)
            return Response({
                'validationMessage': [{
                    'statusCode': 500,
                    'message': 'مشکلی در درخواست شما بوجود آمد'
                }],
                'result': None,
                'resultStatus': 1
            }, status=500)
            

    def retrieve(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            # only some of users (in my test case, superusers) can see all the books even banned books, other users can only see unbanned books
            if book.is_banned:
                if not request.user.is_superuser:
                    return Response({
                        'validationMessage': [{
                            'statusCode': 403,
                            'message': 'شما اجازه دسترسی به این کتاب را ندارید'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=403)
            serializer = BookReadSerializer(instance=book)
            return Response({
                        'validationMessage': [{
                            'statusCode': 200,
                            'message': 'اطلاعات با موفقیت دریافت شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=200)
        except Book.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': 404,
                            'message': 'اطلاعات یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=404)


    @extend_schema(
        request=BookUpdateSerializerRequest
    )
    def update(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)

            if request.data.get('title') != None and request.data['title'] != '':
                book.title = request.data['title']

            if request.data.get('is_banned') != None and request.data['is_banned'] != '':
                if request.data.get('is_banned') == 'true':
                    book.is_banned = True
                elif request.data.get('is_banned') == 'false':
                    book.is_banned = False
                else:
                    return Response({
                        'validationMessage': [{
                            'statusCode': 400,
                            'message': 'مقدار is_banned باید یا true باشد یا false'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=400)
                
            if request.data.get('category') != None and request.data['category'] != '':
                new_category = Category.objects.get(id=request.data['category'])
                book.category = new_category
            
            if request.data.get('book_file') != None and request.data['book_file'] != '':
                book_bucket = BooksBucket()
                book_bucket.deleteFile(book.book_file_url)
                name, extension = os.path.splitext(request.FILES.get('book_file').name)
                rnd_filename = f'{uuid.uuid4()}{extension.lower()}'
                book.book_file_url = rnd_filename
                book_bucket.UploadFile(src_file_path=request.FILES.get('book_file'), filename=rnd_filename)
            
            book.save()
            serializer = BookCreateOrUpdateOrDeleteSerializer(instance=book)
            return Response({
                        'validationMessage': [{
                            'statusCode': 202,
                            'message': 'اطلاعات با موفقیت بروزرسانی شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=202)
        except Book.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': 404,
                            'message': 'اطلاعات یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=404)
        except Category.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': 404,
                            'message': 'کتگوری مورد نظر شما یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=404)


    def destroy(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookCreateOrUpdateOrDeleteSerializer(instance=book)
            book_bucket = BooksBucket()
            book_bucket.deleteFile(book.book_file_url)
            book.delete()
            return Response({
                        'validationMessage': [{
                            'statusCode': 204,
                            'message': 'اطلاعات با موفقیت حذف شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=204)
        except Book.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': 404,
                            'message': 'اطلاعات یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=404)
            

    @extend_schema(
        request=PurchaseBookRequest
    )
    def purchase_book(self, request):
        try:
            if request.data.get('book_id') is None:
                return Response({
                    'validationMessage': [{
                        'statusCode': 400,
                        'message': 'ID کتاب مورد نظرتان را وارد کنید'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=400)

            book = Book.objects.get(pk=request.data['book_id'])

            # only some of users (in my test case, superusers) can see all the books even banned books, other users can only see unbanned books
            if book.is_banned:
                if not request.user.is_superuser:
                    return Response({
                        'validationMessage': [{
                            'statusCode': 403,
                            'message': 'شما اجازه دسترسی به این کتاب را ندارید'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=403)
            serializer = PurchaseBookResponse(book, many=False)
            if not book.purchasers.filter(id=request.user.id):
                book.purchasers.add(User.objects.get(pk=request.user.id))
                if UserWallet.objects.get(user__id=request.user.id).charge < book.price:
                    return Response({
                        'validationMessage': [{
                            'statusCode': 400,
                            'message': 'شما اعتبار کافی در کیف پول خود برای خریدن این کتاب را ندارید'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=400)
                user_wallet = UserWallet.objects.get(user__id=request.user.id)
                user_wallet.charge = user_wallet.charge - book.price

                book.save()
                user_wallet.save()
            else:
                return Response({
                    'validationMessage': [{
                        'statusCode': 200,
                        'message': 'شما این کتاب را از قبل خریده‌اید'
                    }],
                    'result': serializer.data,
                    'resultStatus': 0
                }, status=200)
            return Response({
                'validationMessage': [{
                    'statusCode': 200,
                    'message': 'خرید شما با موفقیت انجام شد'
                }],
                'result': serializer.data,
                'resultStatus': 0
            }, status=200)
        except Book.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': 404,
                            'message': 'کتاب مورد نظر شما یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=404)