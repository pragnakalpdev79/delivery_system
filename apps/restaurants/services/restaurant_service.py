# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.core.cache import cache
from django.db.models import Count
from django.db import transaction

# Local Imports
from apps.restaurants.models import RestrauntModel


logger = logging.getLogger('main')

class RestaurantService:
    @staticmethod
    @transaction.atomic
    def create_resto(**kwargs):
        new_resto = RestrauntModel.objects.create(
            owner = kwargs.get('owner'),
            name = kwargs.get('name'),
            description = kwargs.get('description'),
            cuisine_type = kwargs.get('cuisine_type'),
            address = kwargs.get('address'),
            phone_number = kwargs.get('phone_number'),
            email = kwargs.get('email'),
            logo = kwargs.get('logo'),
            banner = kwargs.get('banner'),
            opening_time = kwargs.get('opening_time'),
            closing_time = kwargs.get('closing_time'),
            delivery_fee = kwargs.get('delivery_fee'),
            minimum_order = kwargs.get('minimum_order'),
            is_open = kwargs.get('is_open'),
        )
        cache.delete('resto_list')
        cache.delete('popular_restos')
        rep = {
            'success': True,
            'message' : "Your restaurant has been successfully registered with us",
            'owner' : new_resto.owner,
            'name' : new_resto.name,
            'description' : new_resto.description,
            'address' : new_resto.address,
        }
