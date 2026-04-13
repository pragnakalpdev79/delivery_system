# Standard Library Imports
import time
import logging

# Third-Party Imports (Django)
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import generics,status,viewsets,filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports
from ....selectors.restaurant_selctor import RestaurantSelector
from ....selectors.menu_selector import MenuSelector
from ....services.restaurant_service import RestaurantService
from ..serializers.restaurants import *
from ....filters import MenuItemFilter,RestaurantFilter
from ....pagination import MenuItemPagination,RestaurantPagination
from apps.users.permissions import IsRestaurantOwner

logger = logging.getLogger('main')

class PerfomanceLoggingMixin:
    def dispatch(self,request,*args,**kwargs):
        start_time = time.time()
        response = super().dispatch(request,*args,**kwargs)
        duration = time.time() - start_time
        logger.info("================================== PERFOMANCE METRICS =======================")
        logger.info(
            f" {request.method} {request.path} - {response.status_code} - {duration:.2f}s"
        )
        return response

#============================================================
# 1.RESTAURANTS VIEWSET 
@extend_schema_view(
    list=extend_schema(
        summary=" R.1 List of all restaurants",
        description="You can get a list of all restaurants available here",
        tags=["Restaurants"],
        responses=RestoListSerializer,
        auth=[],
    ),
    retrieve=extend_schema(
        summary=" R.2 Get details of a restaurant",
        description="Pass the restaurant id to get all details about it",
        tags=["Restaurants"],
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
class RestaurantViewSet(PerfomanceLoggingMixin,viewsets.ModelViewSet):
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
    http_method_names = ['get', 'post','patch','delete']
    pagination_class = RestaurantPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name','cuisine_type','description']
    ordering_fields = ['average_rating','delivery_fee','created_at']
    ordering = ['-average_rating']
    filterset_class = RestaurantFilter

    queryset = RestrauntModel.objects.filter(deleted_at=None)

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

        print("none")
        return RestoListSerializer
    
    def get_permissions(self):
        print(self.action)
        if self.action == 'list':
            return [AllowAny()]
        if self.action == 'create':
            logger.info("Create action detected")
            return [IsRestaurantOwner()]
        if self.action == 'partial_update':
            return [IsRestaurantOwner()]
        if self.action == 'deleter':
            return [IsRestaurantOwner()]
        return [IsAuthenticatedOrReadOnly()]
    
#==============================================================================
# 1. GET ALL RESTAURANTS BY GET METHOOD
    def list(self,request):
        listofresto = RestaurantSelector.get_resto_list()
        page = self.paginate_queryset(listofresto)
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            logger.info("Listing all restaurants- Paginated")
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(listofresto,many=True)
        logger.info("Listing all restaurants")
        return Response(serializer.data)


    
#==============================================================================
# 2. GET ONE RESTAURANT BY ITS ID
    def retrieve(self, request, pk=None):
        resto = RestaurantSelector.get_resto(pk=pk)
        serializer = self.get_serializer(resto)
        return Response({
            "message" : "Here are the restaurant details",
            "resto_id" : pk,
            'details' : serializer.data,
        })
#==============================================================================
# 3. REGISTER A NEW RESTAURANT - BY OWNER ONLY
    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RestaurantService.create_resto(owner=request.user,**serializer.validated_data)
        
        return Response(
            {
            'success': True,
            'message' : "Your restaurant has been successfully registered with us",
            'data' : serializer.validated_data,
        },
        status=status.HTTP_201_CREATED)



#==============================================================================
# 4. GET MENU ITEMS OF A SPECIFC RESTAURANT IF YOU HAVE RESTO ID
    @action(detail=True,methods=['get'],
            pagination_class=MenuItemPagination)
    def menu(self,request,pk=None):
        #DONE
        queryset = MenuSelector.get_menu_list(pk=pk)
        self.filterset_class = MenuItemFilter
        self.search_fields = ['name','description']
        self.ordering_fields = ['price','name','created_at']
        self.ordering = ['name']
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            logger.info("p1")
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)
    
        serializer = self.get_serializer(queryset,many=True)
        logger.info("listing all menu items")

        if not serializer.data:
            msg = "The requested menu does not exist"
            st = status.HTTP_404_NOT_FOUND
        else:
            msg = "Here is the menu for restaurant"
            st = status.HTTP_200_OK

        return Response({
            "message" : msg,
            "id": pk,
            "menu" : serializer.data,
        },
        status = st)
    
#==============================================================================
# 5. POPULAR RESTOS - CACHED 30 MIN
    @action(detail=False,methods=['get'])
    def popular(self,request):
        cache_key = 'popular_restos'
        cached = cache.get(cache_key)

        if cached:
            logger.info("returning cached popular restos")
            return Response(cached)
        
        queryset = RestaurantSelector.get_popular()
        serializer = self.get_serializer(queryset,many=True)
        cache.set(cache_key,serializer.data,1800)  # 30 minutes
        logger.info("listing popular restos and caching")
        return Response(serializer.data)

#==============================================================================
# 6. DELETE A RESTO + CACHE INVALIDATION
    @action(detail=True,methods=['delete'])
    def deleter(self,request,pk):
        print(request.user)
        #resto = self.get_queryset().get(id=pk)
        resto = RestaurantSelector.get_resto(pk=pk)
        if resto.owner != request.user:
            return Response({
                "error" : "not allowed",
            },status = status.HTTP_403_FORBIDDEN)
        print(type(resto))
        resto.delete()
        cache.delete('resto_list')
        cache.delete(f'resto_{pk}')
        cache.delete(f'menuof__{pk}')
        cache.delete('popular_restos')
        logger.info("cache cleared after restaurant delete")
        return Response({"message" : "restaurnt deleted",
                         "id": str(resto.id) 
                         })

#==============================================================================
# 7. UPDATE RESTAURANT - CACHE INVALIDATION ON PATCH

    def partial_update(self,request,pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response({
            "message" : "Works",
            "requested" : pk,
            'data': serializer.data,
        })

    def perform_update(self,serializer):

        instance = serializer.save()
        cache.delete('resto_list')
        cache.delete(f'resto_{instance.pk}')
        cache.delete('popular_restos')
        logger.info(f"cache cleared after restaurant update {instance.pk}")