# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save

# Local Imports
from apps.users.models import CustomUser,CustomerProfile,DriverProfile

logger = logging.getLogger('main')

@receiver(post_save,sender=CustomUser)
def post_save_user(sender,instance,created,**kwargs):
    if created:
        if instance.check_if_customer:
            logger.info("A customer registered")
            newprofile = CustomerProfile.objects.create(user=instance)
            logger.info(f"New Customer Profile for {instance.email} Completed!!")
        if instance.check_if_restaurant:
            logger.info("A restaurant owner registered")
        if instance.check_if_driver:
            newprofile = DriverProfile.objects.create(user=instance,vehicle_number=f"Temp_{instance.phone_number[-3:]}",license_number=f"TempL_{instance.phone_number[-3:]}")
            logger.info(f"New Driver Profile for {instance.email} Completed!!")
