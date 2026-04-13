import factory
import logging
from factory.django import DjangoModelFactory
from decimal import Decimal

from apps.users.models import CustomUser, address, CustomerProfile
from common.models.driver import DriverProfile
from apps.restaurants.models import RestrauntModel, MenuItem
from apps.orders.models import CartItem, Order, OrderItem, Review

logger = logging.getLogger('main')

class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = "Test"
    last_name = "User"
    phone_number = factory.Sequence(lambda n: f"+91990000{n:02d}")
    utype = "c"
    password = factory.PostGenerationMethodCall("set_password", "pass12345")


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = address

    adrname = factory.Sequence(lambda n: f"Home-{n}")
    address = "Test Address, City"
    is_default = True
    adrofuser = factory.SubFactory(CustomUserFactory, utype="c")
    latitude = Decimal("23.0225")
    longitude = Decimal("72.5714")


class CustomerProfileFactory(DjangoModelFactory):
    class Meta:
        model = CustomerProfile

    user = factory.SubFactory(CustomUserFactory, utype="c")


class DriverProfileFactory(DjangoModelFactory):
    class Meta:
        model = DriverProfile

    logger.info("test")
    user = factory.SubFactory(CustomUserFactory, utype="d")
    vehicle_number = factory.Sequence(lambda n: f"GJ01AB{n:04d}")
    #logger.info(vehicle_number)
    license_number = factory.Sequence(lambda n: f"LIC{n:06d}")
    #logger.info(license_number)
    is_available = True


class RestaurantFactory(DjangoModelFactory):
    class Meta:
        model = RestrauntModel

    owner = factory.SubFactory(CustomUserFactory, utype="r")
    name = factory.Sequence(lambda n: f"Resto-{n}")
    description = "Good food"
    cuisine_type = "in"
    address = "Resto Street"
    phone_number = factory.Sequence(lambda n: f"+91980000{n:04d}")
    email = factory.Sequence(lambda n: f"resto{n}@example.com")
    opening_time = "09:00"
    closing_time = "23:00"
    delivery_fee = Decimal("30.00")
    minimum_order = Decimal("100")
    average_rating = Decimal("0.0")


class MenuItemFactory(DjangoModelFactory):
    class Meta:
        model = MenuItem

    restaurant = factory.SubFactory(RestaurantFactory)
    name = factory.Sequence(lambda n: f"Item-{n}")
    description = "Menu item"
    price = Decimal("120.00")
    category = "m"
    dietary_info = "no"
    is_available = True
    preparation_time = 15


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    user = factory.SubFactory(CustomUserFactory, utype="c")
    menu_item = factory.SubFactory(MenuItemFactory)
    quantity = 2


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(CustomUserFactory, utype="c")
    restaurant = factory.SubFactory(RestaurantFactory)
    driver = None
    delivery_address = factory.SubFactory(AddressFactory)
    adratorder = "Delivery Address"
    status = Order.STATE_PD


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    menu_item = factory.SubFactory(MenuItemFactory)
    quantity = 1
    uprice = Decimal("120.00")


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    customer = factory.SubFactory(CustomUserFactory, utype="c")
    restaurant = factory.SubFactory(RestaurantFactory)
    menu_item = factory.SubFactory(MenuItemFactory)
    order = factory.SubFactory(OrderFactory)
    rating = 5
    comment = "Great"
