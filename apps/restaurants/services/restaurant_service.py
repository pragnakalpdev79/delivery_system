# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db.models import Count

# Local Imports
from apps.restaurants.models import RestrauntModel

logger = logging.getLogger('main')

class RestaurantService:
    @staticmethod
    @transaction.atomic
    def create_resto(data):
        new_resto = RestrauntModel.objects.create(

        )
