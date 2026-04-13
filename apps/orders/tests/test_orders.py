import pytest
import logging
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from common.tests.factories import (
    CustomUserFactory,
    AddressFactory,
    RestaurantFactory,
    MenuItemFactory,
    DriverProfileFactory,
)
from apps.orders.models import Order
from rest_framework.test import APIClient

logger = logging.getLogger('main')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestCartAndOrders:
    #TO1 
    def test_add_to_cart_and_view_cart(self, api_client):
        customer = CustomUserFactory(utype="c")
        token = RefreshToken.for_user(customer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")

        resto = RestaurantFactory()
        item = MenuItemFactory(restaurant=resto, is_available=True)

        res_add = api_client.post("/api/v1/orders/cart/addtocart/", {
            "menu_item": item.id,
            "quantity": 2
        }, format="json")
        assert res_add.status_code == status.HTTP_201_CREATED

        res_cart = api_client.get("/api/v1/orders/cart/mycart/")
        assert res_cart.status_code == status.HTTP_200_OK
        assert res_cart.data["item_count"] >= 1

    #TO2
    def test_checkout_confirm_true_creates_order(self, api_client):
        customer = CustomUserFactory(utype="c")
        AddressFactory(adrofuser=customer, is_default=True)

        token = RefreshToken.for_user(customer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")

        resto = RestaurantFactory(minimum_order=50)
        item = MenuItemFactory(restaurant=resto, price=120, is_available=True)

        api_client.post("/api/v1/orders/cart/addtocart/", {
            "menu_item": item.id,
            "quantity": 1
        }, format="json")

        res = api_client.post("/api/v1/orders/cart/checkout/", {
            "confirm": True,
            "special_instructions": "Less spicy"
        }, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1

    #TO3
    def test_assign_driver(self, api_client):
        owner = CustomUserFactory(utype="r")
        logger.info(owner.id)
        customer = CustomUserFactory(utype="c")
        logger.info(customer.id)
        addr = AddressFactory(adrofuser=customer, is_default=True)
        resto = RestaurantFactory(owner=owner)
        logger.info("before error")
        driver = CustomUserFactory(utype="d")
        logger.info(driver.id)

        order = Order.objects.create(
            customer=customer,
            restaurant=resto,
            delivery_address=addr,
            adratorder=addr.address,
        )

        token = RefreshToken.for_user(owner)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")

        res = api_client.post(f"/api/v1/orders/management/{order.order_number}/assign_driver/", {
            "driver_id": str(driver.id)
        }, format="json")

        assert res.status_code == status.HTTP_200_OK
