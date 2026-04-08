# Standard Library Imports
import logging

# Third-Party Imports (Django)
from rest_framework import status
from rest_framework.response import Response

#Local Imports
from apps.orders.models import Order,CartItem
from apps.restaurants.models import MenuItem

logger = logging.getLogger('main')

class CartSelector:
    @staticmethod
    def get_menu_item(menu_item_id):
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
            if not menu_item.is_available:
                raise ValueError('error menu item not found')  
            return menu_item 
                
        except MenuItem.DoesNotExist:
            logger.info("Menu_item does not exists")
            raise ValueError('error menu item not found')
        
    @staticmethod
    def check_if_added_tocart(user,menu_item):
        existing = CartItem.objects.filter(user=user,menu_item=menu_item).first()
        if existing:
            True   
        return False
    