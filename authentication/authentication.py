# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import authenticate as core_auth
from helpers.jwt_helper import JWTHelper
from rest_framework.response import Response

User = get_user_model()

class UserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            if 'HTTP_AUTHORIZATION' in request.META:
                token = request.META.get('HTTP_AUTHORIZATION').replace("Bearer ", "")
                if not token:
                    raise exceptions.AuthenticationFailed('No token provided')
                is_valid, message = JWTHelper.is_token_valid(token)
                if is_valid:
                    username = JWTHelper.decode_token(token)
                    try:
                        user = User.objects.get(phonenumber=username)
                    except User.DoesNotExist:
                        raise exceptions.AuthenticationFailed('No such user')
                    return user, None
                raise exceptions.AuthenticationFailed(message)
            raise exceptions.AuthenticationFailed('No token provided')
        except exceptions.AuthenticationFailed:
            username = request.data.get('phonenumber', None)
            password = request.data.get('password', None)
            try:
                user = User.objects.get(phonenumber=username)
            except Exception as e:
                raise exceptions.AuthenticationFailed(detail='Invalid Token')
            authenticated_user = core_auth(username=username, password=password)
            if authenticated_user:
                return user, None
            raise exceptions.AuthenticationFailed(detail='Invalid Token')
        except Exception as e:
            # print(e)
            # print(type(e))
            pass