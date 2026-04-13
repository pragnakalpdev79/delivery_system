import pytest
import datetime
from decimal import Decimal
from django.utils import timezone
from apps.restaurants.models import RestrauntModel, MenuItem
from common.tests.factories import CustomUserFactory, RestaurantFactory, MenuItemFactory, ReviewFactory

@pytest.mark.django_db
class TestRestaurantModel:
    def test_restaurant_str(self):
        resto = RestaurantFactory(name="Spice Kingdom")
        assert str(resto) == "Spice Kingdom"

    def test_is_currently_open_true(self, mocker):
        resto = RestaurantFactory(
            opening_time=datetime.time(9, 0),
            closing_time=datetime.time(23, 0)
        )
        mock_time = datetime.datetime.combine(datetime.date.today(), datetime.time(14, 0))
        mocker.patch('django.utils.timezone.now', return_value=timezone.make_aware(mock_time))
        assert resto.is_currently_open() is True

    def test_is_currently_open_false(self, mocker):
        resto = RestaurantFactory(
            opening_time=datetime.time(9, 0),
            closing_time=datetime.time(17, 0)
        )
        mock_time = datetime.datetime.combine(datetime.date.today(), datetime.time(20, 0))
        mocker.patch('django.utils.timezone.now', return_value=timezone.make_aware(mock_time))
        assert resto.is_currently_open() is False

    def test_update_average_rating_with_reviews(self):
        resto = RestaurantFactory(average_rating=Decimal('0.0'), total_reviews=0)
        ReviewFactory(restaurant=resto, rating=4)
        ReviewFactory(restaurant=resto, rating=5)
        
        resto.update_average_rating()
        resto.refresh_from_db()
        
        assert resto.average_rating == Decimal('4.5')
        assert resto.total_reviews == 2

    def test_update_average_rating_no_reviews(self):
        resto = RestaurantFactory(average_rating=Decimal('4.0'), total_reviews=1)
        resto.update_average_rating()
        resto.refresh_from_db()
        
        assert resto.average_rating == Decimal('0.0')
        assert resto.total_reviews == 0

    def test_soft_delete(self):
        resto = RestaurantFactory()
        resto.delete()
        resto.refresh_from_db()
        assert resto.deleted_at is not None

    def test_restore(self):
        resto = RestaurantFactory()
        resto.delete()
        resto.restore()
        resto.refresh_from_db()
        assert resto.deleted_at is None


@pytest.mark.django_db
class TestMenuItemModel:
    def test_menu_item_str(self):
        item = MenuItemFactory(name="Paneer Tikka")
        assert str(item) == "Paneer Tikka"
