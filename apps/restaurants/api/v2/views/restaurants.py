# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import status,viewsets,filters
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports
from ....selectors.restaurant_selctor import RestaurantSelector
from ..serializers.restaurants import RestoListSerializer,RestoCreateSerializer,RestoSerializer,MenuItemSerializer,RestoUpdateSerializer 

logger = logging.getLogger('user')

#============================================================
# 1.RESTAURANTS VIEWSET 
@extend_schema_view(
    list=extend_schema(
        summary=" R.1 List of all restaurants - with cache enabled",
        description="You can get a list of all restaurants available here",
        tags=["Restaurants-v2"],
        responses=RestoListSerializer,
        auth=[],
    ),
    retrieve=extend_schema(
        summary=" R.2 Get details of a restaurant - with cache enabled",
        description="Pass the restaurant id to get all details about it",
        tags=["Restaurants-v2"],
        auth=[],
    ),
    create=extend_schema(
        summary="R.3 Register Your restaurant",
        description="Enter your restaurant details and register a new one,this endpoint can be only accesed if you are a restaurnt owner" \
        " [Restaurant Owner Permission Required]",
        tags=["Restaurants"],
        auth=[{"tokenAuth": [], }],
    ),
    menu=extend_schema(
        summary=" R.4 Get Menu from a restaurant id",
        description="Pass Restaurant id to get its menu",
        tags=["Restaurants"],
        auth=[],
    ),
    popular=extend_schema(
        summary=" R.5 Check popular restaurants",
        description="Endpoint to fetch popular restaurants ordered by top rated",
        tags=["Restaurants"],
        auth=[],
    ),
    deleter=extend_schema(
        summary=" R.6 Delete a restaurant",
        description="Can be only accessed if user has restaurant owner permission",
        tags=["Restaurants"],
        auth=[{"tokenAuth": [], }],
    ),
    partial_update=extend_schema(
        summary=" R.7 Update restaurant details",
        description="Can be only accessed if user has restaurant owner permission",
        tags=["Restaurants"],
        auth=[{"tokenAuth": [], }],
    )
)
class RestaurantViewSet(viewsets.ModelViewSet):
    """
    RESTAURANT MANAGEMENT VIEWSET
    HAS FOLLOWING FUNCTIONS
    1. LIST ALL
    2. GET BY ID
    3. REGISTER NEW FOR OWNERS
    4. GET MENU BY RESTAURANT ID
    5. GET POPULAR RESTAURANTS
    6. DELETE YOUR RESTAURANT
    7. UPDATE RESTAURANT DETAILS
    """
    http_method_names = ['get']

    def get_serializer_class(self):
        logger.info(self.action)
        if self.action == 'list':
            return RestoListSerializer
        elif self.action == 'create':
            return RestoCreateSerializer
        elif self.action == 'retrieve':
            return RestoSerializer
        elif self.action == 'menu':
            return MenuItemSerializer
        elif self.action == "partial_update":
            return RestoUpdateSerializer  

        #print("none")
        return RestoListSerializer
    
#==============================================================================
# 1. GET ALL RESTAURANTS BY GET METHOOD
    def list(self,request):
        cache_key = 'resto_list'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            queryset = RestaurantSelector.get_resto_list()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page,many=True)
                cached_data = serializer.data
                cache.set(cache_key,cached_data,300)
                return self.get_paginated_response(serializer.data)
        return Response(cached_data)
#==============================================================================
# 2. GET ONE RESTAURANT BY ITS ID
    def retrieve(self, request, pk=None):
        cache_key = f"resto_{pk}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            resto = RestaurantSelector.get_resto(pk=pk)
            self.check_object_permissions(request,resto)
            serializer = self.get_serializer(resto)
            cached_data = serializer.data
            cache.set(cache_key,cached_data,600)
            return Response({
                    "message" : "Here are the restaurant details",
                    "resto_id" : pk,
                    'details' : serializer.data,
                })
        return Response(cached_data)      
