# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports
from apps.users.models import CustomUser

logger = logging.getLogger('main')

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(**kwargs):
        
        user = CustomUser.objects.create_user(
             email=kwargs.get('email'),
             password=kwargs.get('password'),
             username=kwargs.get('username'),
             first_name=kwargs.get('first_name'),
             last_name=kwargs.get('last_name'),
             utype=kwargs.get('utype'),
             phone_number=kwargs.get('phone_number'),
        )

        if user.check_if_customer:
            group = Group.objects.get(name='Customers')
            user.groups.add(group)
            logger.info(f" {user}==>{group}")

        if user.check_if_restaurant:
            group = Group.objects.get(name='RestrauntOwners')
            user.groups.add(group)
            logger.info(f" {user}==>{group}")

        if user.check_if_driver:
            group = Group.objects.get(name='Drivers')
            user.groups.add(group)
            logger.info(f" {user}==>{group}")

        refresh = RefreshToken.for_user(user)


        rep = {
            'user' : user.email,
            'message' : f"You have been successfully registered as a {group}",
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        }

        return rep