import django_filters
from apps.orders.models import Order, Review

class OrderFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Order
        fields = ['status', 'restaurant', 'created_at__gte']

class ReviewFilter(django_filters.FilterSet):
    class Meta:
        model = Review
        fields = ['rating', 'restaurant', 'menu_item']
