# Standard Library Imports
from __future__ import unicode_literals
import uuid,logging,datetime
from decimal import Decimal
from datetime import timedelta

# Third-Party Imports (Django)
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

#Local Imports
from .managers import MyUserManager
from common.models.timestamped import TimestampedModel
from common.models.softdel import SoftDeleteModel



logger = logging.getLogger('main')


############################################################################
#  1. MAIN USER MODEL EXTENDED FROM ABSTRACTUSER
class CustomUser(AbstractUser,SoftDeleteModel,TimestampedModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False) #UUID
    email = models.EmailField(unique=True) #UNIQUE EMAIL
    first_name = models.CharField(max_length=20) # FIRST NAME
    last_name = models.CharField(max_length=20) # LAST NAME

    USER_TYPE = ( 
        ('c','Customer'),
        ('r','Restaurant Owner'),
        ('d','Delivery Driver   '),
    )
    utype = models.CharField(max_length=1,choices=USER_TYPE,blank=True,default='c',help_text='User Type') #USER TYPE
    deleted_at = models.DateTimeField(null=True,blank=True)
    phone_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999".Up to 15 digits allowed.' 
        )],
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','utype','phone_number']
    objects = MyUserManager()
    all_objects = models.Manager()

    # METHODS TO CHECK TYPE OF USER
    @property
    def check_if_customer(self):
        result = (self.utype == 'c')
        return result
    
    @property
    def check_if_restaurant(self):
        result = (self.utype == 'r')
        return result
    
    @property
    def check_if_driver(self):
        result = (self.utype == 'd')
        return result

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    class Meta: 
        permissions = [
            ('IsOwnerOrReadOnly',"AA owner can edit/delete, others read-only"),
            ('IsRestaurantOwner',"AA only restaurant owner can edit restaurant and menu items"),
            ('IsCustomer',"AA only customers can place orders and write reviews"),
            ('IsDriver',"AA only drivers can update delivery status and location"),
            ('IsOrderCustomer',"AA only order customer can view order details"),
            ('IsRestaurantOwnerOrDriver',"AA restaurant owner or assigned driver can update order status"),
        ]

############################################################################
#  2. ADDRESS MODEL TO STORE ALL ADDRESSES
class address(TimestampedModel):
    adrname = models.CharField(max_length=60,unique=True,help_text='Short name to identify the adress')
    address = models.TextField(help_text='Your full address')
    is_default = models.BooleanField()
    adrofuser = models.ForeignKey('CustomUser',on_delete=models.CASCADE,related_name="user_s_adress")
    latitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,help_text='Latitude')
    longitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,help_text='Longitude')
    location = gis_models.PointField(srid=4326,null=True,blank=True,help_text='coordinates for distance calculation')


    def save(self,*args,**kwargs):
        if self.is_default:
            usradrs = address.objects.filter(adrofuser=self.adrofuser)
            usradrs.update(is_default=False)
        if self.latitude and self.longitude and not self.location:
            self.location = Point(float(self.longitude),float(self.latitude),srid=4326)
            logger.info(f"location point created: {self.location}")
        super().save(*args,**kwargs)

    def __str__(self):
        return f"User : {self.adrofuser}, Adress saved as : {self.adrname}, Full Address:  {self.address}"

############################################################################
#  3.CUSTOMER PROFILE
class CustomerProfile(TimestampedModel):
    user = models.OneToOneField('CustomUser',on_delete=models.RESTRICT,related_name='customer_profile',primary_key=True)
    avatar = models.ImageField(upload_to='user_avatars/',blank=True,null=True)
    loyalty_points = models.IntegerField(default=0)

    @property
    def default_adress(self):
        defadr = address.objects.get(adrofuser=self.user,is_default=True)
        return defadr

    @property
    def saved_addresses(self):
        alladrs = address.objects.filter(adrofuser=self.user)
        return alladrs

    @property
    def total_orders(self):
        return self.user.order_for.count()
    
    @property
    def total_spend(self):
        spend = self.user.order_for.filter(status='dl')
        spend = spend.aggregate(total=Sum('total_amount'))
        if spend['total']:
            return spend['total']
        return Decimal('0.00')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

############################################################################
#  4.DRIVER PROFILE
class DriverProfile(TimestampedModel):
    user = models.OneToOneField('CustomUser',on_delete=models.RESTRICT,related_name='driver_profile')
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