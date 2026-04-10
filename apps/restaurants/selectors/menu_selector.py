# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db.models import Count

# Local Imports
from apps.restaurants.models import MenuItem

class MenuSelector:
    @staticmethod
    def get_menu_list(pk):
        queryset = MenuItem.objects.filter(restaurant_id=pk)
        return queryset