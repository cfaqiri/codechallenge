import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class UserTests(TestCase):
    def test_user_registration(self):
        '''Check if we can register a new account'''

        client = APIClient()
        response = client.post(
                '/register/', {
                'email': 'test123@gmail.com',
                'username': 'test_user',
                'password': 'test_password123'
            },
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)    
    