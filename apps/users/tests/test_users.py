import pytest
from django.contrib.auth.models import Group


# Third-Party Imports
from asgiref.sync import async_to_sync,sync_to_async
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient, APITestCase
from rest_framework import status



# Local Imports
from apps.users.models import CustomUser
from common.tests.fixtures import api_client,create_groups,customer
from common.tests.factories import CustomUserFactory


@pytest.mark.django_db
class TestRegistration:
    def test_customer_registration(self,api_client):
        print("=====test1 registration=====")
        data = {
            'email':'newcust@test.com',
            'username':'newcust',
            'password':'strongpass123',
            'password_confirm':'strongpass123',
            'first_name':'New',
            'last_name':'Customer',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/v1/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        print(response)
        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data
    def test_registration_password_mismatch(self,api_client):
        print("=====test2 password mismatch=====")
        data = {
            'email':'fail@test.com',
            'username':'failuser',
            'password':'spass123',
            'password_confirm':'wpass123',
            'first_name':'Fail',
            'last_name':'User',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/v1/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        assert response.status_code == 400
    #DUPLICATE EMAIL
    #DONE
    def test_registration_duplicate_email(self,api_client,customer):
        print("=====test3 duplicate email=====")
        data = {
            'email':'testcust@test.com', #already exists
            'username':'anothercust',
            'password':'strongpass123',
            'password_confirm':'strongpass123',
            'first_name':'Another',
            'last_name':'Customer',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/v1/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        assert response.status_code == 400

# class UserTestCase(APITestCase):
#     def setUp(self):
#         self.user = CustomUserFactory()
#         self.client.force_authenticate(user=self.user)

#     def test_customer_registration(self):
#         print("=====test1 registration=====")
#         response = self.client.post('/api/auth/register/',self.user,format='json')

