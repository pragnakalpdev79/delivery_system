# Standard Library Imports
import logging

# Local Imports
from apps.orders.models import CartItem
from apps.restaurants.models import MenuItem

logger = logging.getLogger('main')


class CartSelector:
    @staticmethod
    def get_menu_item(menu_item_id):
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
            if not menu_item.is_available:
                raise ValueError('menu item not available')
            return menu_item
        except MenuItem.DoesNotExist:
            logger.info("menu item does not exist")
            raise ValueError('menu item not found')

    @staticmethod
    def get_existing_cart_item(user, menu_item):
        return CartItem.objects.filter(user=user, menu_item=menu_item).first()

    @staticmethod
    def get_user_cart(user):
        return CartItem.objects.filter(user=user).select_related('menu_item', 'menu_item__restaurant')

    @staticmethod
    def clear_user_cart(user):
        return CartItem.objects.filter(user=user).delete()
