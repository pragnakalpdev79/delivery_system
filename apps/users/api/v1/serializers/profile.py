# Standard Library Imports
import logging,re
# Third-Party Imports (Django)
from django.contrib.auth import authenticate
from rest_framework import serializers
from PIL import Image
# Local Imports
from apps.users.models import CustomerProfile,DriverProfile,CustomUser

logger = logging.getLogger('main')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','first_name','last_name','phone_number']

class CustomerProfileSerializerv(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['user','avatar','loyalty_points']
        

class CustomProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerProfile
        fields = ['user','avatar','total_orders','loyalty_points']
        read_only_fields = ['loyalty_points']

    
    def validate_avatar(self,value):
        if value:
            if value.size > 5*1024*1024:
                raise serializers.ValidationError("Image size cannot exceed 5mb")
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg','jpeg','png']:
                raise serializers.ValidationError("Only jpg, jpeg, png allowed")
        try:
            img = Image.open(value)
            img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid Image format")
        return value
    
class DriverProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = DriverProfile
        fields = ['user','avatar','vehicle_number','license_number','']
