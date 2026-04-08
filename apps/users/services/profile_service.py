# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports
from apps.users.models import CustomerProfile

logger = logging.getLogger('main')

class ProfileService:
    @staticmethod
    @transaction.atomic
    def update_profile(muser,**kwargs):
        try:
            print("data",kwargs)
            profile = CustomerProfile.objects.select_related('user').get(user=muser)
            for key,value in kwargs:
                setattr(profile,key,value)
            profile.save()
            return kwargs
        except CustomerProfile.DoesNotExist:
            return {
                "error" : "The Requested Profile Does Not Exists", 
            }
        
    
