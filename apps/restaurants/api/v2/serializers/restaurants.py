# Standard Library Imports
import logging
import datetime

# Third-Party Imports (Django)
from rest_framework import serializers
from PIL import Image

# Local Imports
from apps.restaurants.models import RestrauntModel,MenuItem



logger = logging.getLogger('user')

class RestoListSerializer(serializers.ModelSerializer):
    logger.info("in serializer")
    is_open_now = serializers.SerializerMethodField()

    class Meta:
        model = RestrauntModel
        fields = ['id','name','description','cuisine_type','address',
                  'phone_number','email','logo','banner','delivery_fee',
                  'is_open_now','minimum_order',
                  'average_rating','total_reviews']
    
    def get_is_open_now(self,obj): #TO CHECK IF THE RESTO IS OPEN OR NOT AT GIVEN TIME
        logger.info(f"======================{datetime.datetime.now().time()}=================")
        if obj.opening_time <= datetime.datetime.now().time() <= obj.closing_time:
            logger.info('Restro is Open')
            return True
        logger.info('Restro is Closed')
        return False
    
class MenuListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name','description','price','category','dietary_info','is_available','preparation_time']
        model = MenuItem

class RestoSerializer(serializers.ModelSerializer):
    menu = MenuListSerializer(many=True)
    class Meta:
        fields = ['name','description','cuisine_type','is_open','opening_time','closing_time','menu','review_for']
        model = RestrauntModel