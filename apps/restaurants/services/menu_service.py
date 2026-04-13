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
        restoid = kwargs.pop('restoid')
        new_menu = MenuItem.objects.create(
            restaurant_id=restoid,
            name=kwargs.get('name'),
            description=kwargs.get('description'),
            price=kwargs.get('price'),
            category=kwargs.get('category'),
            dietary_info=kwargs.get('dietary_info'),
            is_available=kwargs.get('is_available',True),
            preparation_time=kwargs.get('preparation_time',3),
            foodimage=kwargs.get('foodimage'),
        )
        cache.delete(f'menuof__{restoid}')
        cache.delete('resto_list')
        logger.info(f"menu item created: {new_menu.name} for restaurant {restoid}")
        return new_menu
