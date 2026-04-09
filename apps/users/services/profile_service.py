# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.db import transaction

# Local Imports
from apps.users.models import CustomerProfile
from common.models.driver import DriverProfile

logger = logging.getLogger('main')


class ProfileService:
    @staticmethod
    @transaction.atomic
    def update_profile(muser, **kwargs):
        #DONE
        try:
            profile = CustomerProfile.objects.select_related('user').get(user=muser)
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.save()
            return profile
        except CustomerProfile.DoesNotExist:
            return None
        
    @staticmethod
    @transaction.atomic
    def update_dprofile(muser, **kwargs):
        #DONE
        try:
            profile = DriverProfile.objects.select_related('user').get(user=muser)
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.save()
            return profile
        except DriverProfile.DoesNotExist:
            return None
