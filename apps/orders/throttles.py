from rest_framework.throttling import ScopedRateThrottle

class OrderCreateThrottle(ScopedRateThrottle):
    scope = 'order_create'

class ReviewCreateThrottle(ScopedRateThrottle):
    scope = 'review_create'

class LocationUpdateThrottle(ScopedRateThrottle):
    scope = 'location_update'
