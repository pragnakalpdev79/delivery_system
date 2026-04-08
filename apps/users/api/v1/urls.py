from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import auth,profile

router = DefaultRouter()
router.register('register',auth.UserRegistrationView,basename='register')
router.register('login',auth.UserLoginView,basename='login')
router.register('logout',auth.UserLogoutView,basename='logout')
router.register('customer_profile',profile.CustomerProfileView,basename='profile')

urlpatterns = [
    path('',include(router.urls)),
]