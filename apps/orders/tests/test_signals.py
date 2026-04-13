import pytest
import logging
from asgiref.sync import async_to_sync
from apps.orders.models import Order
from common.tests.factories import CustomUserFactory, RestaurantFactory, OrderFactory, DriverProfileFactory
from common.models.driver import DriverProfile

logger = logging.getLogger('main')

@pytest.mark.django_db
class TestSignals:
    def test_driver_delivery_stats_updated_on_delivery(self):
        driver_user = CustomUserFactory(utype='d')
        #dp = DriverProfileFactory(user=driver_user, total_deliveries=0)
        
        order = OrderFactory(status=Order.STATE_PU, driver=driver_user)
        dp = driver_user.driver_profile
        # Transition to DL should trigger signal
        order.delivered()
        
        dp.refresh_from_db()
        assert dp.total_deliveries == 1
