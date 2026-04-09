from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import cart

router = DefaultRouter()
router.register('cart', cart.CartViewSet, basename='cart')
router.register('management', cart.OrderViewSet, basename='orders-management')
router.register('reviews', cart.ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]
