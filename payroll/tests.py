from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase

from django.contrib.auth.models import User 

client = APIClient()

class UserTestCase(TestCase):
    def setUp(self):
        user = User(
            email='testing_login@cosasdedevs.com',
            username='Testing',
        )
        user.set_password('admin123')
        user.save()
    
    