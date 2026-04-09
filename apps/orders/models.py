# Standard Library Imports
from __future__ import unicode_literals
import uuid,logging,datetime
from decimal import Decimal
from datetime import timedelta

# Third-Party Imports (Django)
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import MaxValueValidator,MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg,Sum,F
from django.utils import timezone

#Local Imports
from common.models.timestamped import TimestampedModel
from common.models.softdel import SoftDeleteModel
from apps.users.models import CustomUser,address
from apps.restaurants.models import RestrauntModel,MenuItem


logger = logging.getLogger('main')




############################################################################
#  7. Order Model
class Order(TimestampedModel):
    customer = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,related_name='order_for',db_index=True)
    restaurant = models.ForeignKey(RestrauntModel,on_delete=models.DO_NOTHING,related_name='order_by',db_index=True)
    driver = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,related_name='deliver_by',null=True)
    order_number = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    STATE_PD = 'pd'
    STATE_CO = 'co'
    STATE_PR = 'pr'
    STATE_RD = 'rd'
    STATE_PU = 'pu'
    STATE_DL = 'dl'
    STATE_CD = 'cd'

    __current_status = None

    SC = (
        (STATE_PD,'Pending'),
        (STATE_CO,'Confiremd'),
        (STATE_PR,'Preparing'),
        (STATE_RD,'Ready'),
        (STATE_PU,'Picked Up'),
        (STATE_DL,'Delivered'),
        (STATE_CD,'Cancelled'),
    )
    TRANSITIONS = {
        STATE_PD: [STATE_CO,STATE_CD],
        STATE_CO: [STATE_PR,STATE_CD],
        STATE_PR: [STATE_RD,STATE_CD],
        STATE_RD: [STATE_PU,STATE_CD],
        STATE_PU: [STATE_DL],
        STATE_DL: [],
        STATE_CD: [],
    }
    status = models.CharField(
        max_length=2,
        choices= SC,
        help_text = 'Order Status',
        db_index=True,
        default=STATE_PD,
    )
    adratorder = models.TextField()
    delivery_address = models.ForeignKey(address,on_delete=models.DO_NOTHING,related_name='delivery_adress')
    subtotal = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
    delivery_fee = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
    special_instructions = models.TextField(null=True,blank=True)
    estimated_delivery_time = models.DateTimeField(null=True,blank=True)
    actual_delivery_time = models.DateTimeField(null=True,blank=True)

    def calculate_total(self,tax_rate=Decimal('0.05')):
        self.subtotal = self.item_for.aggregate(
            total=Sum(F('uprice') * F('quantity'))
        )['total'] or Decimal('0.00')
        self.delivery_fee = self.restaurant.delivery_fee
        self.tax = (self.subtotal * tax_rate).quantize(Decimal('0.01'))
        self.total_amount = self.subtotal + self.delivery_fee + self.tax
        self.save(update_fields=['subtotal','delivery_fee','tax','total_amount'])
        logger.info(f"Order total:-- sub = {self.subtotal} ---- tax={self.tax} ----- total={self.total_amount}")

    def calculate_eta(self):
        """
        Calculate estimated delivery time based on distance between
        restaurant and delivery address using geodjango.
        Assumes 40 km/h average delivery speed.
        """
        logger.info("calculating ETA ")
        resto_location = self.restaurant.location
        delivery_location = self.delivery_address.location

        if not resto_location or not delivery_location:
            logger.info("location data not found")
            self.estimated_delivery_time = timezone.now() + timedelta(minutes=30) # 30 MIN DEFAULT 
            self.save(update_fields=['estimated_delivery_time'])
            return

        distance_m = resto_location.distance(delivery_location) * 100000  # degrees to meters approx
        distance_km = distance_m / 1000
        logger.info(f"distance: {distance_km:.2f} km")
        SPEED_KMH = 40
        travel_hours = distance_km / SPEED_KMH
        travel_minutes = max(int(travel_hours * 60),5)  # minimum 5 min
        max_prep = self.item_for.aggregate(
            max_prep=models.Max('menu_item__preparation_time')
        )['max_prep'] or 15
        logger.info(f"max prep time: {max_prep} min")
        total_minutes = travel_minutes + max_prep
        self.estimated_delivery_time = timezone.now() + timedelta(minutes=total_minutes)
        self.save(update_fields=['estimated_delivery_time'])
        logger.info(f"ETA == {self.estimated_delivery_time} ({total_minutes} min = {travel_minutes} travel + {max_prep} prep)")

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__current_status = self.status #INTIATED WITH PENDING ORDER STATUS
    
    def save(self, force_insert=False, 
             force_update=False, 
             using=None,
             update_fields=None): 
        # CHECKS IF THE MODEL IS BEING CREATED OR UPDATED
        #IF THE STATE IS CHANGED ITS UPDATED HENCE SKIP VALIDATION
        # self.status(pending) != self.__current_status(pending) which means it is not updated yet. hence False(Not Updated)
        logger.info("step1")
        allowed_next = self.TRANSITIONS.get(self.__current_status,[]) 
        logger.info("step2")
        updated = self.status != self.__current_status
        logger.info("step3")

        if self.pk and updated and self.status not in allowed_next:
            #raise Exception("Invalid Transition.",self.status,allowed_next)
            raise ValidationError(
                f"Invalid Transition: {self.__current_status} -> {self.status} -- Allowed = {allowed_next}"
            )
        
        logger.info("step4")

        if self.pk and updated:
            self.__current_status = self.status

        logger.info("step5")

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
    
    def _transition(self,next_status):
        logger.info("step6")
        self.status = next_status
        logger.info("step7")
        if next_status == self.STATE_DL:
            self.actual_delivery_time = timezone.now()
        self.save()
        logger.info(f"Order {self.order_number} transitioned to {next_status}")

    def raccept(self,driver=None):
        self._transition(self.STATE_CO)

    def rreject(self):
        self._transition(self.STATE_CD)

    def confiremd(self):
        self._transition(self.STATE_PR)

    def readytop(self):
        self._transition(self.STATE_RD)

    def pickedup(self):
        self._transition(self.STATE_PU)

    def delivered(self):
        self._transition(self.STATE_DL)

    @property
    def is_cancellable(self):
        return self.status in [self.STATE_PD,self.STATE_CO,self.STATE_PR,self.STATE_RD]

    @property
    def is_completed(self):
        return self.status in [self.STATE_DL,self.STATE_CD]
    
    def can_cancel(self):
        return self.status in [self.STATE_PD,self.STATE_CO,self.STATE_PR,self.STATE_RD]
    
    def is_delivered(self):
        return self.status == self.STATE_DL 

############################################################################
#  8. Cart-Items Model
class CartItem(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='user_cart')
    menu_item = models.ForeignKey(MenuItem,on_delete=models.DO_NOTHING,related_name='added_item')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"This is {self.user}'s cart for - {self.menu_item} with quantity {self.quantity}"

############################################################################
#  9. Order-Item Model
class OrderItem(models.Model):
    order = models.ForeignKey('Order',on_delete=models.DO_NOTHING,related_name='item_for')
    menu_item = models.ForeignKey(MenuItem,on_delete=models.DO_NOTHING,related_name='item_from')
    quantity = models.PositiveIntegerField(blank=False,null=False)
    uprice = models.DecimalField(max_digits=5,decimal_places=2,help_text='snapshot of item price at order time')
    special_instructions = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Order Item details : {self.menu_item} | Quantity : {self.quantity} | Special Instructions provided : {self.special_instructions}" 

############################################################################
#  10. Cart Model
class Review(TimestampedModel):
    customer = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='review_by')
    restaurant = models.ForeignKey(RestrauntModel,on_delete=models.CASCADE,related_name='review_for',null=True)
    menu_item = models.ForeignKey(MenuItem,on_delete=models.CASCADE,related_name='review_of',null=True)
    order = models.ForeignKey('Order',on_delete=models.CASCADE,related_name='order')
    rating = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField(null=True)

    def clean(self):
        if self.order.customer != self.customer:
            raise ValidationError("you can only review your own orders")
        if self.order.status != 'dl':
            raise ValidationError("can not review the orders which are not delivered")
        
    def __str__(self):
        return f"Review by {self.customer.email} for menu-item {self.menu_item} is {self.rating},which was order the {self.restaurant} "