# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.core.cache import cache
from django.db.models import Count
from django.db import transaction

# Local Imports
from apps.restaurants.models import MenuItem

logger = logging.getLogger('main')

class MenuService:
    @staticmethod
    @transaction.atomic
    def create_menu_item(**kwargs):
        new_menu = MenuItem.objects.create(
            restoid= ,
            name= ,
            desciption= ,
            price= ,
            category= ,
            dietary_info= ,
            is_avaialable= ,
            preparation_time= ,
            food_image=
        )