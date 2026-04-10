from django.contrib import admin
from .models import RestrauntModel,MenuItem

@admin.register(RestrauntModel)
class RestrauntModel(admin.ModelAdmin):
    list_display = ('name','email','phone_number','owner','cuisine_type','description','id','location')
    ordering = ['-created_at']


@admin.register(MenuItem)
class MenuItem(admin.ModelAdmin):
    list_display = ('name','restaurant','category','description','id')
    ordering = ['-created_at']