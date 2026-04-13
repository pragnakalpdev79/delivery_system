import pytest
from decimal import Decimal
from apps.orders.services.order_services import CartService
from apps.orders.models import CartItem, Order
from common.tests.factories import CustomUserFactory, RestaurantFactory, MenuItemFactory, AddressFactory

@pytest.mark.django_db
class TestCartService:
    def test_update_cart_new_item(self):
        #DONE
        user = CustomUserFactory()
        resto = RestaurantFactory()
        item = MenuItemFactory(restaurant=resto)
        
        CartService.update_cart(user, item, 2)
        assert CartItem.objects.filter(user=user).count() == 1
        assert CartItem.objects.get(user=user).quantity == 2

    def test_update_cart_existing_item(self):
        #DONE
        user = CustomUserFactory()
        resto = RestaurantFactory()
        item = MenuItemFactory(restaurant=resto)
        
        CartService.update_cart(user, item, 1)
        CartService.update_cart(user, item, 2)
        
        assert CartItem.objects.get(user=user).quantity == 3

    def test_checkout_empty_cart_raises_error(self):
        #DONE
        user = CustomUserFactory()
        with pytest.raises(ValueError, match="cart is empty"):
            CartService.checkout(user)

    def test_checkout_multiple_restaurants_raises_error(self):
        #DONE
        user = CustomUserFactory()
        resto1 = RestaurantFactory()
        resto2 = RestaurantFactory()
        item1 = MenuItemFactory(restaurant=resto1)
        item2 = MenuItemFactory(restaurant=resto2)
        
        CartService.update_cart(user, item1, 1)
        CartService.update_cart(user, item2, 1)
        
        with pytest.raises(ValueError, match="all items must belong to same restaurant"):
            CartService.checkout(user)
