import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.users.models import CustomUser,CustomerProfile,Address
from common.models.driver import DriverProfile
from common.tests.fixtures import create_groups
from django.db.models import Avg,Count,Sum,F

@pytest.fixture
def customer_user(db):
    return CustomUser.objects.create_user(
        email='cust@test.com',password='pass12345',
        username='custuser',first_name='Test',last_name='Customer',
        phone_number='+919900001111',utype='c'
    )

@pytest.fixture
def driver_user(db):
    return CustomUser.objects.create_user(
        email='drv@test.com',password='pass12345',
        username='drvuser',first_name='Test',last_name='Driver',
        phone_number='+919900002222',utype='d'
    )

@pytest.fixture
def resto_user(db):
    return CustomUser.objects.create_user(
        email='resto@test.com',password='pass12345',
        username='restouser',first_name='Test',last_name='Owner',
        phone_number='+919900003333',utype='r'
    )


@pytest.mark.django_db
class TestCustomUser:
    def test_user_type_flags_customer(self,customer_user):
        assert customer_user.check_if_customer is True
        assert customer_user.check_if_restaurant is False
        assert customer_user.check_if_driver is False

    def test_user_type_flags_driver(self,driver_user):
        assert driver_user.check_if_driver is True
        assert driver_user.check_if_customer is False

    def test_user_type_flags_restaurant(self,resto_user):
        assert resto_user.check_if_restaurant is True
        assert resto_user.check_if_customer is False

    def test_str_representation(self,customer_user):
        assert customer_user.email in str(customer_user)

    def test_soft_delete(self,customer_user):
        customer_user.delete()
        assert customer_user.deleted_at is not None
        #default manager filters deleted
        assert CustomUser.objects.filter(email='cust@test.com').count() == 0
        #all_objects still returns it
        assert CustomUser.all_objects.filter(email='cust@test.com').count() == 1

    def test_restore_after_soft_delete(self,customer_user):
        customer_user.delete()
        customer_user.restore()
        assert customer_user.deleted_at is None
        assert CustomUser.objects.filter(email='cust@test.com').count() == 1


@pytest.mark.django_db
class TestCustomerProfile:
    def test_profile_auto_created_on_customer_signup(self,customer_user):
        #signal should create CustomerProfile
        assert CustomerProfile.objects.filter(user=customer_user).exists()

    def test_profile_not_created_for_driver(self,driver_user):
        assert not CustomerProfile.objects.filter(user=driver_user).exists()

    def test_default_loyalty_points(self,customer_user):
        profile = CustomerProfile.objects.get(user=customer_user)
        assert profile.loyalty_points == 0

    def test_total_orders_zero_initially(self,customer_user):
        profile = CustomerProfile.objects.annotate(total_order=Count("user__order_for"),total_spent=Sum("user__order_for__total_amount")).select_related('user').get(user=customer_user)
        #profile = CustomerProfile.objects.get(user=customer_user)
        assert profile.total_order == 0

    def test_total_spend_zero_initially(self,customer_user):
        profile = CustomerProfile.objects.annotate(total_order=Count("user__order_for"),total_spent=Sum("user__order_for__total_amount")).select_related('user').get(user=customer_user)
        #profile = CustomerProfile.objects.get(user=customer_user)
        assert profile.total_spent == None


@pytest.mark.django_db
class TestDriverProfile:
    def test_driver_profile_auto_created(self,driver_user):
        assert DriverProfile.objects.filter(user=driver_user).exists()

    def test_default_availability(self,driver_user):
        dp = DriverProfile.objects.get(user=driver_user)
        assert dp.is_available is True

    def test_update_availability(self,driver_user):
        dp = DriverProfile.objects.get(user=driver_user)
        dp.update_availability(False)
        dp.refresh_from_db()
        assert dp.is_available is False

    def test_get_delivery_stats(self,driver_user):
        dp = DriverProfile.objects.get(user=driver_user)
        stats = dp.get_delivery_stats()
        assert stats['total_deliveries'] == 0
        assert stats['is_available'] is True


@pytest.mark.django_db
class TestAddress:
    def test_create_address(self,customer_user):
        adr = Address.objects.create(
            adrname='Home',address='123 Street',
            is_default=True,adrofuser=customer_user,
        )
        assert adr.pk is not None

    def test_default_address_resets_others(self,customer_user):
        adr1 = Address.objects.create(
            adrname='Home',address='123 Street',
            is_default=True,adrofuser=customer_user,
        )
        adr2 = Address.objects.create(
            adrname='Office',address='456 Avenue',
            is_default=True,adrofuser=customer_user,
        )
        adr1.refresh_from_db()
        assert adr1.is_default is False
        assert adr2.is_default is True
