from rest_framework import serializers
from django.contrib.auth import get_user_model
from helpers.jwt_helper import JWTHelper

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phonenumber', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('token',)

    def get_token(self, user):
        user = JWTHelper.encode_token(user)
        return user

class UserSignupSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phonenumber', 'password']
    
class UserLoginSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phonenumber', 'password']