# Standard Library Imports
import logging
import datetime


# Third-Party Imports (Django)
from rest_framework import serializers
from PIL import Image
from django.utils import timezone

# Local Imports
from apps.restaurants.models import RestaurantModel, MenuItem

logger = logging.getLogger('main')


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'category', 'dietary_info', 'is_available', 'preparation_time', 'foodimage']


class RestoListSerializer(serializers.ModelSerializer):
    is_open_now = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantModel
        fields = ['id', 'name', 'description', 'cuisine_type', 'address', 'phone_number', 'email',
                  'logo', 'banner', 'delivery_fee', 'minimum_order', 'average_rating', 'total_reviews', 'is_open_now']

    def get_is_open_now(self, obj):
        now = timezone.localtime(timezone.now()).time()
        return obj.opening_time <= now <= obj.closing_time



class RestoSerializer(serializers.ModelSerializer):
    menu = MenuItemSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantModel
        fields = ['id', 'owner', 'name', 'description', 'cuisine_type', 'address', 'phone_number', 'email',
                  'logo', 'banner', 'opening_time', 'closing_time', 'is_open', 'delivery_fee', 'minimum_order',
                  'average_rating', 'total_reviews', 'menu', 'reviews_count']
        read_only_fields = ['owner', 'average_rating', 'total_reviews']

    def get_reviews_count(self, obj):
        return obj.review_for.count()


class RestoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantModel
        fields = ['owner','name','description','cuisine_type','address','phone_number','email','logo','banner',
                  'opening_time','closing_time','delivery_fee','minimum_order','latitude','longitude','location']
        read_only_fields = ['owner']


    def validate_logo(self, value):
        if not value:
            return value
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Logo size cannot exceed 5MB")
        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png']:
            raise serializers.ValidationError("Only jpg, jpeg, png allowed")
        try:
            img = Image.open(value); img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid logo image")
        return value

    def validate_banner(self, value):
        if not value:
            return value
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Banner size cannot exceed 10MB")
        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png']:
            raise serializers.ValidationError("Only jpg, jpeg, png allowed")
        try:
            img = Image.open(value); img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid banner image")
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class RestoUpdateSerializer(RestoCreateSerializer):
    class Meta(RestoCreateSerializer.Meta):
        pass
