# Third-Party Imports (Django)
from django.urls import path,include
from rest_framework.routers import DefaultRouter

# Local Imports
from .views import restaurants,menu

router = DefaultRouter()
router.register('details',restaurants.RestaurantViewSet,basename='restaurants')
router.register('menu_details',menu.MenuItemViewSet,basename='menus')

urlpatterns = [
    path('',include(router.urls)),
]