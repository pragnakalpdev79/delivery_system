# Third-Party Imports (Django)
from django.urls import path,include
from rest_framework.routers import DefaultRouter

# Local Imports
from .views import restaurants

router = DefaultRouter()
router.register('details',restaurants.RestaurantViewSet,basename='restaurants')

urlpatterns = [
    path('',include(router.urls)),
]