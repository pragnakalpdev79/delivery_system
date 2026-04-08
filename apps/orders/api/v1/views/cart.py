# Standard Library Imports
import logging
from datetime import timedelta

# Third-Party Imports (Django)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status,viewsets,filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.response import Response

# Local Imports
# from .throttles import *
from ....selectors.orders_selectors import CartSelector
from ....services.order_services import CartService
# from .filters import OrderFilter,ReviewFilter 
# from user.permissions import IsRestaurantOwner,IsCustomer,IsDriver,IsRestaurantOwnerOrDriver
# from .serializers import *
# from .pagination import OrdersPagination,ReviewPagination

logger = logging.getLogger('main')

extrap = extend_schema(
        tags=["extra"],
    )


class CartViewSet(viewsets.ModelViewSet):
    """
    Cart View set has the following functionsx
    1. Menu-items can be addes to the cart with post request
    2. Cart can be viewed
    3. Clear cart
    4. checkout -- 
        4.1 if confirm= False it will just show cart total and all
        4.2 if confirm= True it acts as mock payment and converts cart to order
    """

    @action(detail=True,methods=['post'])
    def addtocart(self,request,pk=None):
        logger.info("called")
        menu_item_id = request.data.get('menu_item')
        logger.info("menu_item-id ",menu_item_id)
        menu_item = CartSelector.get_menu_item(menu_item_id)
        logger.info("menu_item",menu_item)
        quantity = int(request.data.get('quantity'))

        existing_cart = CartSelector.check_and_add(request.user,menu_item=menu_item,quantity=quantity)

        if existing_cart:
           cart = CartService.

        if "error" in menu_item:
            return menu_item
        return Response({
            "error" : "under progresss",
        })
        