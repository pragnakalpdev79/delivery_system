# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db.models import Count

# Local Imports
from apps.restaurants.models import RestaurantModel

class RestaurantSelector:
    @staticmethod
    def get_resto_list(): #.prefetch_related('menu')
        #queryset = RestaurantModel.objects.filter(deleted_at=None).annotate(items_count=Count('menu'))
        queryset = RestaurantModel.objects.defer('description', 'created_at', 'updated_at').annotate(items_count=Count('menu'))
        return queryset
    
    @staticmethod
    def get_resto(pk):
        queryset = RestaurantModel.objects.prefetch_related('review_for','menu').get(id=pk)
        return queryset
    
    @staticmethod
    def get_popular():
        queryset = RestaurantModel.objects.order_by('-total_reviews')
        return queryset
        