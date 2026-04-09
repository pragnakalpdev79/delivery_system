import logging
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

logger = logging.getLogger('main')

#P1 GENERAL OWNER
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "owner_id", None) == request.user.id

#P2 RESTO OWNER ONLY
class IsRestaurantOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.utype == 'r'

#P3 CUSTOMER ONLY
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.utype == 'c'

#P4 DRIVER ONLY
class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.utype == 'd'

#P5 CUSTOMER WHO ORDERED
class IsOrderCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.customer_id == request.user.id

# RESTO OR DRIVER OF THE ORDER
class IsRestaurantOwnerOrDriver(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if getattr(obj.restaurant, "owner_id", None) == request.user.id:
            return True
        if getattr(obj, "driver_id", None) == request.user.id:
            return True
        return False
