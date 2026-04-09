from rest_framework.pagination import PageNumberPagination

class RestaurantPagination(PageNumberPagination):
    page_size = 20

class MenuItemPagination(PageNumberPagination):
    page_size = 30
