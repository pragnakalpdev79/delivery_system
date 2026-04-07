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
from common.tests.fixtures import api_client
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
        response = api_client.post('/api/v1/users/register/',data,format='json')
        print(f"response -- {response.status_code}")
        print(response)
        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data

class UserTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUserFactory()
        