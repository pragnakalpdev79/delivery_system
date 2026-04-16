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
from django.db.models import Avg 

#Local Imports
from apps.restaurants.managers import MyRestoManager
from common.models.timestamped import TimestampedModel
from common.models.softdel import SoftDeleteModel
from apps.users.models import CustomUser


logger = logging.getLogger('main')

############################################################################
#  5.Restaurant-Model
class RestaurantModel(TimestampedModel,SoftDeleteModel):
    owner = models.ForeignKey(CustomUser,on_delete=models.RESTRICT,related_name='Restaurant_owner')
    name = models.CharField(max_length=50)
    description = models.TextField()
    CC = (
        ('it','Italian'),
        ('ch','Chinese'),
        ('in','Indian'),
        ('me','Mexican'),
        ('am','American'), 
        ('ja','Japanese'),
        ('th','Thai'),
        ('md','Mediterranean'),
    )
    cuisine_type = models.CharField(max_length=2,choices=CC,help_text='Available Cuisine')
    address = models.TextField()
    phone_number = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999".Up to 15 digits allowed.' ,
        )],)
    email = models.EmailField(unique=True) 
    logo = models.ImageField(upload_to='logos/',blank=True,null=True)
    banner = models.ImageField(upload_to='banners/',blank=True,null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_open = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=4,decimal_places=2)
    minimum_order = models.DecimalField(default=0,decimal_places=0,max_digits=3)
    average_rating = models.DecimalField(max_digits=2,default=0,decimal_places=1)
    total_reviews = models.IntegerField(null=True,blank=True)
    #deleted_at = models.DateTimeField(null=True,blank=True)
    latitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,help_text='Latitude of restaurant')
    longitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True,help_text='Longitude of restaurant')
    location = gis_models.PointField(srid=4326,null=True,blank=True,help_text='GPS coordinates for distance calculation')

    def save(self,*args,**kwargs):
        #=====================================
        # AUTO-CREATE POINT FROM LAT/LNG
        #=====================================
        if self.latitude and self.longitude and not self.location:
            self.location = Point(float(self.longitude),float(self.latitude),srid=4326)
            logger.info(f"restaurant location point created: {self.location}")
        super().save(*args,**kwargs)

    def is_currently_open(self):
        now = timezone.localtime(timezone.now()).time()
        result = self.opening_time <= now <= self.closing_time
        logger.info(f"{self.name} is_currently_open: {result}")
        return result

    
    def update_average_rating(self):
        avg = self.review_for.aggregate(avg=Avg('rating'))['avg']
        if avg:
            self.average_rating = round(avg,1)
            self.total_reviews = self.review_for.count()
            self.save(update_fields=['average_rating','total_reviews'])
            logger.info(f"updated rating for {self.name} to {self.average_rating}")

    # #@property
    # def delete(self,using=None,keep_parents=False):
    #     print("deleting")
    #     self.deleted_at = timezone.now()
    #     self.save(update_fields=["deleted_at"])
    
    # #@property
    # def restore(self):
    #     self.deleted_at = None
    #     self.save(update_fields=["deleted_at"])
    objects = MyRestoManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        indexes = [
                models.Index(fields=["owner","deleted_at"],name='activeresto')
            ]

############################################################################
#  6. Menu-Items Model
class MenuItem(TimestampedModel):
    restaurant = models.ForeignKey('RestaurantModel',on_delete=models.CASCADE,related_name='menu')
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    CAC = (
        ('a','Appteizer'),
        ('m','Main Course'),
        ('d','Desert'),
        ('b','Beverage'),
        ('s','Side Dish'),
    )
    category = models.CharField(
        max_length = 1,
        choices = CAC,
        help_text = 'Available Catagories',
    )
    DIC = (
        ('v1','Vegetarian'),
        ('v2','Vegan'),
        ('gf','Gluten-Free'),
        ('df','Dairy-Free'),
        ('no','None'),
    )
    dietary_info = models.CharField(
        max_length=2,
        choices = DIC,
        help_text= 'Diteray information',
    )
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(default=3)


    def file_path(self):
        return f"{self.name}/menu_items"
    
    foodimage = models.ImageField(upload_to=file_path,blank=True,null=True)

    def __str__(self):
        return f"{self.name}"