from rest_framework.pagination import CursorPagination, LimitOffsetPagination

class OrdersPagination(CursorPagination):
    """
    Cursor Pagination for Order List

    Query Parameters : 
    - ordering 
    - page_size

    Response includes count, next, previous, and results array.
    """
    page_size = 25
    ordering = '-created_at'

class ReviewPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 50
