from rest_framework.pagination import CursorPagination, LimitOffsetPagination

class OrdersPagination(CursorPagination):
    page_size = 25
    ordering = '-created_at'

class ReviewPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 50
