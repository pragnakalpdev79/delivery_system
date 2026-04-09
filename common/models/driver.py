# Standard Library Imports
from __future__ import unicode_literals
import logging

# Third-Party Imports (Django)

from django.contrib.gis.geos import Point
from django.db import models



#Local Imports
from common.models.timestamped import TimestampedModel
from apps.orders.models import Order
from apps.users.models import CustomUser


logger = logging.getLogger('main')

############################################################################
#  4.DRIVER PROFILE
class DriverProfile(TimestampedModel):
    
    user = models.OneToOneField(CustomUser,on_delete=models.RESTRICT,related_name='driver_profile')
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    VTYPE = (
        ('b','Bike'),
        ('s','Scooter'),
        ('c','Car'),
    )
    vehicle_type = models.CharField(max_length=1,choices=VTYPE,blank=True,default='b',help_text="Delivery partner's Vehicle Type")
    vehicle_number = models.CharField(max_length=10,unique=True)
    license_number = models.CharField(max_length=10,unique=True)
    is_available = models.BooleanField(default=True)
    total_deliveries = models.IntegerField(blank=True,null=True)
    average_rating = models.DecimalField(max_digits=2,decimal_places=1,default=0)

    def update_availability(self,available=True):
        #changing availability directly from this function
        self.is_available = available
        self.save(update_fields=['is_available'])
        logger.info(f"driver availability set to {available}")


    def get_delivery_stats(self):
        # get all delivered orders of requested user
        delivered = Order.objects.filter(driver=self.user,status='dl').count()
        logger.info(f"delivery stats for {self.user.email}: {delivered}")
        return {
            'total_deliveries': delivered,
            'average_rating': self.average_rating,
            'is_available': self.is_available,
        }