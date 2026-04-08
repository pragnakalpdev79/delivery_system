# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db import transaction

#Local Imports
from apps.orders.models import Order,CartItem
from apps.restaurants.models import MenuItem

logger = logging.getLogger('main')

class CartService:
    @staticmethod
    @transaction.atomic
    def update_cart(user,menu_item,quantity):
        