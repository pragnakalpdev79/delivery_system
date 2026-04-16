from apps.users.models import CustomerProfile
from common.models.driver import DriverProfile
from django.db.models import Avg,Count,Sum,F

class ProfileSelector:
    @staticmethod
    def get_user_profile(ruser):
        #DONE
        #.annotate(Sum("user__order_for"))
        #.select_related('user')
        #.prefetch_related("user__order_for")
        cp = CustomerProfile.objects.annotate(total_order=Count("user__order_for"),total_spent=Sum("user__order_for__total_amount")).select_related('user').get(user=ruser)
        return cp
    
    
    @staticmethod
    def get_driver_profile(duser):
        #DONE
        return DriverProfile.objects.select_related('user').get(user=duser)
    