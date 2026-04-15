# Standard Library Imports
import logging

# Third-Party Imports (Django)
from PIL import Image
from rest_framework import serializers

# Local Imports
from apps.users.models import CustomerProfile, CustomUser
from common.models.driver import DriverProfile

logger = logging.getLogger('main')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number']


class CustomerProfileSerializerv(serializers.ModelSerializer):
    user = CustomerSerializer(read_only=True)
    total_order = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        model = CustomerProfile
        #, 'total_orders', 'total_spend'
        fields = ['user', 'avatar', 'loyalty_points','total_order','total_spent']


class CustomProfileSerializer(serializers.ModelSerializer):
    #DONE
    class Meta:
        model = CustomerProfile
        fields = ['avatar']

    def validate_avatar(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image size cannot exceed 5mb")
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise serializers.ValidationError("Only jpg, jpeg, png allowed")
            try:
                img = Image.open(value)
                img.verify()
            except Exception:
                raise serializers.ValidationError("Invalid Image format")
        return value


class DriverProfileSerializer(serializers.ModelSerializer):
    #DONE
    class Meta:
        model = DriverProfile
        fields = ['avatar', 'vehicle_number', 'license_number', 'is_available']
       

class DriverProfileSerializeru(serializers.ModelSerializer):
    #DONE
    class Meta:
        model = DriverProfile
        fields = ['avatar', 'vehicle_number', 'license_number', 'is_available']

    def validate_avatar(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image size cannot exceed 5mb")
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise serializers.ValidationError("Only jpg, jpeg, png allowed")
            try:
                img = Image.open(value)
                img.verify()
            except Exception:
                raise serializers.ValidationError("Invalid Image format")
        return value
