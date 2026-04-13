from django.contrib import admin
from .models import RestaurantModel,MenuItem

@admin.register(RestaurantModel)
class RestaurantModel(admin.ModelAdmin):
    list_display = ('name','email','phone_number','owner','cuisine_type','description','id','location')
    ordering = ['-created_at']


@admin.register(MenuItem)
class MenuItem(admin.ModelAdmin):
    list_display = ('name','restaurant','category','description','id')
    ordering = ['-created_at']