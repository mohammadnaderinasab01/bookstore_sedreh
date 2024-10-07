from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.serializers import UserSerializer


class UserRegistrationAPITests(APITestCase):

    def setUp(self):

        self.user_dict = {
            'first_name': 'mohammad',
            'last_name': 'naderi',
            'phonenumber': 'mohammad_naderi@gmail.com',
            'password': 'mohammad_password',
        }

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('register')
        data = self.user_dict
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['phonenumber'], self.user_dict['phonenumber'])

    def test_phonenumber_already_exists(self):
        """
        Ensure we can't have duplicate phonenumbers.
        """
        url = reverse('register')
        data = self.user_dict
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """
        Ensure we can login with a valid user.
        """
        serializer = UserSerializer(data=self.user_dict)
        if serializer.is_valid():
            serializer.save()

        url = reverse('login')
        data = {
            "phonenumber": self.user_dict['phonenumber'],
            "password": self.user_dict['password'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_credentials(self):
        """
        Ensure we can't login with invalid credentials.
        """
        serializer = UserSerializer(data=self.user_dict)
        if serializer.is_valid():
            serializer.save()

        url = reverse('login')
        data = {
            "phonenumber": self.user_dict['phonenumber'],
            "password": 'mohammad_password',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLoginAPITests(APITestCase):

    def setUp(self):

        self.user_dict = {
            'first_name': 'mohammad',
            'last_name': 'naderi',
            'phonenumber': 'mohammad_naderi@gmail.com',
            'password': 'mohammad_password',
        }

        serializer = UserSerializer(data=self.user_dict)
        if serializer.is_valid():
            serializer.save()

    def test_login_user(self):
        """
        Ensure we can login with a valid user.
        """
        url = reverse('login')
        data = {
            "phonenumber": self.user_dict['phonenumber'],
            "password": self.user_dict['password'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_credentials(self):
        """
        Ensure we can't login with invalid credentials.
        """
        url = reverse('login')
        data = {
            "phonenumber": self.user_dict['phonenumber'],
            "password": 'mohammad_password',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
