import pytest
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.orders.models import Order, CartItem, OrderItem
from common.tests.factories import CustomUserFactory, RestaurantFactory, MenuItemFactory, AddressFactory

@pytest.mark.django_db
class TestOrderModel:
    @pytest.fixture
    def setup_order(self):
        #DONE
        customer = CustomUserFactory(utype='c')
        resto = RestaurantFactory(delivery_fee=Decimal('30.00'))
        addr = AddressFactory(adrofuser=customer)
        item1 = MenuItemFactory(restaurant=resto, price=Decimal('100.00'), preparation_time=10)
        item2 = MenuItemFactory(restaurant=resto, price=Decimal('150.00'), preparation_time=20)
        
        order = Order.objects.create(
            customer=customer,
            restaurant=resto,
            delivery_address=addr,
            adratorder=addr.address
        )
        OrderItem.objects.create(order=order, menu_item=item1, quantity=2, uprice=item1.price)
        OrderItem.objects.create(order=order, menu_item=item2, quantity=1, uprice=item2.price)
        
        return order

    def test_calculate_total(self, setup_order):
        #DONE
        order = setup_order
        order.calculate_total(tax_rate=Decimal('0.05'))
        
        # Subtotal: (100 * 2) + (150 * 1) = 350.00
        # Tax: 350 * 0.05 = 17.50
        # Delivery: 30.00
        # Total: 350 + 17.50 + 30 = 397.50
        assert order.subtotal == Decimal('350.00')
        assert order.tax == Decimal('17.50')
        assert order.delivery_fee == Decimal('30.00')
        assert order.total_amount == Decimal('397.50')

    def test_state_transitions(self, setup_order):
        #DONE
        order = setup_order
        assert order.status == Order.STATE_PD
        order.raccept()
        assert order.status == Order.STATE_CO
        order.confiremd()
        assert order.status == Order.STATE_PR
        order.readytop()
        assert order.status == Order.STATE_RD
        order.pickedup()
        assert order.status == Order.STATE_PU
        order.delivered()
        assert order.status == Order.STATE_DL

    def test_invalid_state_transition(self, setup_order):
        #DONE
        order = setup_order
        with pytest.raises(ValidationError):
            order.status = Order.STATE_DL  # Cannot jump from PD to DL
            order.save()

    def test_cancellation_allowed(self, setup_order):
        #DONE
        order = setup_order
        assert order.can_cancel() is True
        order.raccept()
        assert order.can_cancel() is True

    def test_cancellation_denied_after_pickup(self, setup_order):
        #DONE
        order = setup_order
        order.status = Order.STATE_PU
        
        assert order.can_cancel() is False
