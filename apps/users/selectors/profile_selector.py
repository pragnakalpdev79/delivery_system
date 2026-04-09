from apps.users.models import CustomerProfile
from common.models.driver import DriverProfile

class ProfileSelector:
    @staticmethod
    def get_user_profile(ruser):
        #DONE
        return CustomerProfile.objects.select_related('user').get(user=ruser)
    
    @staticmethod
    def get_driver_profile(duser):
        #DONE
        return DriverProfile.objects.select_related('user').get(user=duser)
    