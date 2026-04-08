# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db.models import Count

# Local Imports
from apps.restaurants.models import RestrauntModel

class RestaurantSelector:
    @staticmethod
    def get_resto_list():
        queryset = RestrauntModel.objects.filter(deleted_at=None).annotate(items_count=Count('menu'))
        return queryset
    
    @staticmethod
    def get_resto():
        queryset = RestrauntModel.objects.prefetch_related('menu','review_for').get(id=pk)
        return queryset