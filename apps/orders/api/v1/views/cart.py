# Standard Library Imports
import logging

# Third-Party Imports (Django)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view,OpenApiResponse
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Local Imports
from apps.orders.models import CartItem, Order, OrderItem, Review,CustomUser
from common.models.driver import DriverProfile
from apps.orders.filters import OrderFilter, ReviewFilter
from apps.orders.pagination import OrdersPagination, ReviewPagination
from apps.orders.throttles import OrderCreateThrottle, ReviewCreateThrottle
from apps.users.permissions import IsCustomer, IsRestaurantOwnerOrDriver
from ....selectors.orders_selectors import CartSelector
from ....services.order_services import CartService
from ..serializers.orders import (
    CartItemSerializer, OrderSerializer, OrderStatusUpdateSerializer, ReviewSerializer
)


logger = logging.getLogger('main')

extrap = extend_schema(
        tags=["extra"],
    )

@extend_schema_view(
    addtocart=extend_schema(
        summary="C.1 ADD TO CART",
        description="Add an item to the cart before checkout to place order.",
        tags=["Cart"],  
        responses=CartItemSerializer,
    ),
    mycart=extend_schema(
        summary="C.2 View cart with total",
        description="This endpoint returns whatever is in the cart and empty if not",
        tags=["Cart"],
    ),
    checkout=extend_schema(
        summary=" C.4 Checkout ",
        description="Confirm Payment here with confirm=true used as mock payment",
        tags=["Cart"],
        responses={
            201 : OpenApiResponse(
                response=OrderSerializer,
                description="Order Confirmed and placed"
            ),
            200 : OpenApiResponse(
                description="review order and set confirm=true"
            ),
            400 : OpenApiResponse(description='Bad request (something invalid)'),
        }
    ),
)
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('menu_item', 'menu_item__restaurant')

   #==================================================================================
    # 1.1 add to cart - if item already exists just update quantity
    @action(detail=False, methods=['post'])
    def addtocart(self, request):
        #DONE
        menu_item_id = request.data.get('menu_item')
        quantity = int(request.data.get('quantity', 1))
        try:
            menu_item = CartSelector.get_menu_item(menu_item_id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = CartService.update_cart(request.user, menu_item, quantity)
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    #==================================================================================
    # 1.2 view full cart with total
    @action(detail=False, methods=['get'])
    def mycart(self, request):
        #DONE
        qs = self.get_queryset()
        return Response({
            'items': CartItemSerializer(qs, many=True).data,
            'cart_total': str(CartService.cart_total(request.user)),
            'item_count': qs.count(),
        })

    #==================================================================================
    # 1.3 clear the ENTIRE CART
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        #DONE
        removed = CartSelector.clear_user_cart(request.user)[0]
        return Response({'message': f'cart cleared, {removed} items removed'})

    #==================================================================================
    # 1.4 CHECKOUT - CONVERT CART TO ORDER MOCK PAYMENT
    @action(detail=False, methods=['post'], throttle_classes=[OrderCreateThrottle])
    def checkout(self, request):
        confirm = request.data.get('confirm', False)
        special = request.data.get('special_instructions', '')

        if not confirm:
            return Response({
                'message': 'review order and set confirm=true',
                'cart_total': str(CartService.cart_total(request.user)),
            },status=status.HTTP_200_OK)

        try:
            order = CartService.checkout(request.user, special_instructions=special)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"restaurant_{order.restaurant_id}",
            {"type": "send.notification",
            "message": f"New order placed: {order.order_number}"},
        )
        async_to_sync(channel_layer.group_send)(
            f"customer_{order.customer_id}",
            {"type": "send.notification",
            "message": f"Order placed: {order.order_number}"},
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

#===============================================================================================
# ORDER VIEWSET - view/manage orders
@extend_schema_view(
    update_status = extend_schema(
        summary=" O.1 UPDATE ORDER STATUS",
        description="Update the order status from confirmed to delivered,can be accessed by driver and restaurant owners",
        auth=[{"tokenAuth": [], }],
        tags=["Order"],
    ),
    assign_driver=extend_schema(
        summary=" O.2 Assign orders to driver",
        description="Orders can accept the new orders from here order id must be passed into request",
        auth=[{"tokenAuth": [], }],
        tags=["Order"],
    ),
    cancel=extend_schema(
        summary=" O.3 Cancel Order",
        description="Cancel order from this endpoint if allowed at given time",
        auth=[{"tokenAuth": [], }],
        tags=["Order"],
    ),
    active=extend_schema(
        summary=" O.4 List of active orders of user",
        description="Returns active orders of logged in user -- for customers only",
        tags=["Order"],
    ),
    history=extend_schema(
        summary=" O.5 Past orders",
        description="Returns Customer's past completed orders -- for customers only",
        auth=[{"tokenAuth": [], }],
        tags=["Order"],
    ),
    destroy = extrap,
    partial_update = extrap,
    update = extrap,
    retrive = extrap,
    create = extrap,
    list = extrap,
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrdersPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('customer', 'restaurant', 'driver').prefetch_related('item_for__menu_item')
        if user.check_if_customer:
            return qs.filter(customer=user)
        if user.check_if_driver:
            return qs.filter(driver=user)
        if user.check_if_restaurant:
            return qs.filter(restaurant__owner=user)
        return qs.none()

    @action(detail=True, methods=['patch'],permission_classes=[IsRestaurantOwnerOrDriver])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data, context={'order': order})
        serializer.is_valid(raise_exception=True)
        order._transition(serializer.validated_data['status'],order.status)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        
        order = self.get_object()
        if request.user.utype != 'r':
            return Response({'error': 'Only restaurant owner can assign driver'}, status=status.HTTP_403_FORBIDDEN)

        if order.restaurant.owner_id != request.user.id:
           return Response({'error': 'You can only assign drivers to your own restaurant orders'}, status=status.HTTP_403_FORBIDDEN)


        driver_id = request.data.get('driver_id')
        try:
            driver = CustomUser.objects.get(id=driver_id, utype='d')
            dp = DriverProfile.objects.get(user=driver)
        except Exception:
            return Response({'error': 'driver not found'}, status=status.HTTP_404_NOT_FOUND)

        if not dp.is_available:
            return Response({'error': 'driver busy'}, status=status.HTTP_400_BAD_REQUEST)

        order.driver = driver
        order.save(update_fields=['driver'])
        dp.is_available = False
        dp.save(update_fields=['is_available'])
        return Response({'message': f'driver {driver.email} assigned'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        qs = self.get_queryset().exclude(status__in=[Order.STATE_DL,Order.STATE_CD])
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs,many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        qs = self.get_queryset().filter(status__in=[Order.STATE_DL,Order.STATE_CD])
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs,many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.customer_id != request.user.id:
            return Response({'error': 'only the customer can cancel their order'}, status=status.HTTP_403_FORBIDDEN)
        if not order.can_cancel():
            return Response({'error': 'order can not be cancelled now'}, status=status.HTTP_400_BAD_REQUEST)
        order.rreject()
        return Response({'message': 'order cancelled'})



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    pagination_class = ReviewPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    throttle_classes = [ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.select_related('customer', 'restaurant', 'menu_item', 'order')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
