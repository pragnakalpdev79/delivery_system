# Standard Library Imports
import logging
import datetime

# Third-Party Imports (Django)
from rest_framework import serializers
from PIL import Image

# Local Imports
from apps.restaurants.models import MenuItem,RestrauntModel

logger = logging.getLogger('main')

class MenuSerializer(serializers.ModelSerializer):
    restoid = serializers.IntegerField()  
    
    class Meta:
        fields = ['restoid','foodimage','name','description','price','category','dietary_info','is_available','preparation_time']
        model = MenuItem


    def validate_foodimage(self,value):

        if value:
            if value.size > 5*1024*1024:
                raise serializers.ValidationError("Image size cannot exceed 5mb")
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg','jpeg','png']:
                raise serializers.ValidationError("Only jpg, jpeg, png allowed")

        return value

    def validate_restoid(self,value):

        id = self.context.get('request').user.id
        try:
            self.resto = RestrauntModel.objects.filter(owner_id=id).get(id=value)
        except RestrauntModel.DoesNotExist:
            raise serializers.ValidationError("Please enter the restaurant which you own and does exits")
        return value