# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db import transaction

# Local Imports
from apps.users.models import CustomerProfile
from common.models.driver import DriverProfile

logger = logging.getLogger('main')

class ProfileService:
    CUSTOMER_UPDATABLE_FIELDS = {'avatar'}
    DRIVER_UPDATABLE_FIELDS = {'avatar','vehicle_number','license_number','is_available','vehicle_type'}

    @staticmethod
    @transaction.atomic
    def update_profile(muser, **kwargs):
        try:
            profile = CustomerProfile.objects.select_related('user').get(user=muser)
            for key, value in kwargs.items():
                if key in ProfileService.CUSTOMER_UPDATABLE_FIELDS:
                    setattr(profile, key, value)
            profile.save()
            return profile
        except CustomerProfile.DoesNotExist:
            return None
        
    @staticmethod
    @transaction.atomic
    def update_dprofile(muser, **kwargs):
        try:
            profile = DriverProfile.objects.select_related('user').get(user=muser)
            for key, value in kwargs.items():
                if key in ProfileService.DRIVER_UPDATABLE_FIELDS:
                    setattr(profile, key, value)
            profile.save()
            return profile
        except DriverProfile.DoesNotExist:
            return None

