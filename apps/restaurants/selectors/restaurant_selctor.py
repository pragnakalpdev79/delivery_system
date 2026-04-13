# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db.models import Count

# Local Imports
from apps.restaurants.models import RestrauntModel

class RestaurantSelector:
    @staticmethod
    def get_resto_list():
        #queryset = RestrauntModel.objects.filter(deleted_at=None).annotate(items_count=Count('menu'))
        queryset = RestrauntModel.objects.filter(deleted_at=None).defer('description', 'created_at', 'updated_at').annotate(items_count=Count('menu'))
        return queryset
    
    @staticmethod
    def get_resto(pk):
        queryset = RestrauntModel.objects.prefetch_related('menu','review_for').get(id=pk)
        return queryset
    
    @staticmethod
    def get_popular():
        queryset = RestrauntModel.objects.order_by('-total_reviews')
        return queryset
        