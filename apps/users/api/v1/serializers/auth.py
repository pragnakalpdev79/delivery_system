# Standard Library Imports
import logging,re
# Third-Party Imports (Django)
from django.contrib.auth import authenticate
from rest_framework import serializers
# Local Imports
from apps.users.models import CustomUser


logger = logging.getLogger('main')


#===============================================================
# SIGN UP SERIALIZER
class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    """
    USER SIGN UP/REGISTRATION 
    - Validates Phone number
    - Validates 2 input passwords if they are same or not
    """
    
    password = serializers.CharField(min_length=8,)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['username','email','phone_number','password','password_confirm','first_name','last_name','utype']
    
    def validate_phone_number(self,value):
        regexf = r'^\+?1?\d{9,15}$'
        if not re.match(regexf,value):
            raise serializers.ValidationError("Please enter the phone number in proper format")
        return value

    def validate(self,data): 
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords dont match")
        data.pop('password_confirm')
    
        if 'utype' not in data:
            raise serializers.ValidationError('Please specify customer Type')

        return data

    
#===============================================================
# LOGIN VIEW SERIALIZER
class CustomUserLoginSerializer(serializers.ModelSerializer):
    """
    Basic login serializer which validates email with authenticate()
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email','password']

    def validate(self,data):
        user = authenticate(email=data['email'],password=data['password'])
        if not user:
            raise serializers.ValidationError("Please enter correct email and password")
        data['user'] = user
        return data