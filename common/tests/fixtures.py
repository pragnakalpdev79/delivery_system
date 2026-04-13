# Standard Library Imports
import pytest

#Third-Party Imports
from asgiref.sync import async_to_sync,sync_to_async
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import CustomUser


@pytest.fixture(autouse=True)
def create_groups(db):
    cgrps,created = Group.objects.get_or_create(name='Customers')
    Group.objects.get_or_create(name='RestaurantOwners')
    Group.objects.get_or_create(name='Drivers')
    print("groups created for test")
    content_type = ContentType.objects.get_for_model(CustomUser)
    customer_permissions = Permission.objects.filter(content_type=content_type,
                                                     codename__in =['IsCustomer'])
    cgrps.permissions.set(customer_permissions)
    

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def customer(db):
    user = CustomUser.objects.create_user(
        email='testcust@test.com',
        password='testpass123',
        username='testcust',
        first_name='Test',
        last_name='Customer',
        phone_number='+919999999990',
        utype='c'
    )
    print(f"created customer -- {user.has_perms}")
    return user