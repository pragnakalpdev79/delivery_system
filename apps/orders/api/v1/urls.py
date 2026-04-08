from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import cart

router = DefaultRouter()
router.register('management',cart.CartViewSet,basename='cart')

urlpatterns = [
    path('',include(router.urls)),
]