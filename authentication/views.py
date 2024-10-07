from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.serializers import UserSerializer, UserLoginSerializer, UserSignupSerializerRequest, UserLoginSerializerRequest
from drf_spectacular.utils import extend_schema


class RegistrationView(APIView):
    @extend_schema(
        request=UserSignupSerializerRequest
    )
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'validationMessage': [{
                        'statusCode': status.HTTP_201_CREATED,
                        'message': 'ثبت نام شما با موفقیت انجام شد'
                    }],
                    'result': serializer.data,
                    'resultStatus': 0
                }, status=status.HTTP_201_CREATED)
            elif serializer.errors != None and serializer.errors.get('phonenumber') != None and serializer.errors.get('phonenumber')[0] != None and str(serializer.errors.get('phonenumber')[0]) == 'user with this phonenumber already exists.':
                return Response({
                    'validationMessage': [{
                        'statusCode': status.HTTP_400_BAD_REQUEST,
                        'message': 'کاربری با این مشخصات از قبل وجود دارد'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': str(e)
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': str(e)
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        request=UserLoginSerializerRequest
    )
    def post(self, request):
        username = request.data.get('phonenumber', None)
        password = request.data.get('password', None)

        authenticated_user = authenticate(username=username, password=password)
        if authenticated_user:
            serializer = UserLoginSerializer(authenticated_user)
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_200_OK,
                    'message': 'شما با موفقیت وارد شدید'
                }],
                'result': serializer.data,
                'resultStatus': 0
            }, status=status.HTTP_200_OK)
        return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_401_UNAUTHORIZED,
                    'message': 'شماره تلفن یا رمز عبورتان را بدرستی وارد نکردید'
                }],
                'result': None,
                'resultStatus': 1
        }, status=status.HTTP_401_UNAUTHORIZED)