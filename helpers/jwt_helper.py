# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.conf import settings
import jwt

User = get_user_model()

class JWTHelper:
    """
    JWT Helper contains utility methods for dealing with JWTokens.

    - JWT_TOKEN_EXPIRY: No. of days
    - JWT_ALGORITHM: Algorithm specified by JWT

    """
    JWT_ALGORITHM = 'HS256'
    JWT_UTF = 'utf-8'
    JWT_TOKEN_EXPIRY = getattr(settings, 'JWT_TOKEN_EXPIRY', 7)

    @staticmethod
    def encode_token(user):
        """
        Token created against username of the user.
        """
        if user:
            data = {
                "exp": datetime.utcnow() + timedelta(days=JWTHelper.JWT_TOKEN_EXPIRY),
                "username": user.phonenumber,
            }
            token = jwt.encode(data, 'secret', algorithm=JWTHelper.JWT_ALGORITHM)
            return token
        raise User.DoesNotExist

    @staticmethod
    def is_token_valid(token):
        """
        Check if token is valid.
        """
        try:
            jwt.decode(token, 'secret', algorithms=JWTHelper.JWT_ALGORITHM)
            return True, "Valid"
        except jwt.ExpiredSignatureError:
            return False, "Token Expired"
        except jwt.InvalidTokenError:
            return False, "Token is Invalid"

    @staticmethod
    def decode_token(token):
        """
        return user for the token given.
        """
        username_dict = jwt.decode(token, 'secret', algorithms=JWTHelper.JWT_ALGORITHM)
        return User.objects.filter(phonenumber=username_dict["username"]).first()