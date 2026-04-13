
# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics,status,viewsets,filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


# Local Imports

from apps.users.permissions import IsRestaurantOwner
from ..serializers.menu import MenuSerializer,MenuListSerializer,MenuUSerializer
from ....filters import MenuItemFilter
from ....services.menu_service import MenuService

logger = logging.getLogger('user')

#==============================================================================
#==============================================================================
# MENU ITEM VIEWSET

@extend_schema_view(
    list=extend_schema(
        summary=" M.1 List menu items",
        description="List all menu items for the restaurant owner",
        tags=["Menu Items"],
        auth=[{"tokenAuth": [], }],
    ),
    create=extend_schema(
        summary=" M.2 Add new menu item",
        description="Add a new menu item to your restaurant",
        tags=["Menu Items"],
        auth=[{"tokenAuth": [], }],
    ),
    partial_update=extend_schema(
        summary=" M.3 Update menu item",
        description="Update details of a menu item",
        tags=["Menu Items"],
        auth=[{"tokenAuth": [], }],
    ),
)
class MenuItemViewSet(viewsets.ModelViewSet):
    """
    MENU-ITEM VIEWSET
    HAS FOLLOWING FUNCTIONS
    1. CREATE
    2. UPDATE
    3. DELETE
    """

    permission_classes = [IsRestaurantOwner]
    filterset_class = MenuItemFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name','description']
    ordering_fields = ['price','name','created_at']
    ordering = ['name']
    #http_method_names = ['get', 'post','patch']

    #queryset = MenuItem.objects.all() 


    def get_serializer_class(self):
        logger.info(self.action)
        if self.action == 'list':
            return MenuListSerializer
        elif self.action == 'create':
            return MenuSerializer
        elif self.action == "partial_update":
            return MenuUSerializer

    # def get_queryset(self):
    #     qs = MenuItem.objects.all()
    #     if self.action == 'list':
    #         resto = RestrauntModel.objects.filter(owner_id=self.request.user).first()
    #         test = qs.filter(restaurant=resto)
    #         return test
    #     if self.action == 'create':
    #         return qs
    
    #post/CREATE MENU - ITEMS
#WORKS    
    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #self.perform_create(serializer)
        menui = MenuService.create_menu_item(**serializer.data)
        return Response({
            "message": "Menu item added successfully",
            "email": request.user.email,
            "Added": serializer.validated_data,
        },status=status.HTTP_201_CREATED)

#WORKS
    def perform_create(self,serializer):
        mid = serializer.validated_data.pop('restoid')
        print(mid)
        serializer.save(restaurant_id=mid)
        cache.delete(f'menuof__{mid}')
        cache.delete('resto_list')
        logger.info(f"cache cleared after new menu item for resto {mid}")
#PATCH-PARTIAL_UPDATE

    def partial_update(self, request, pk=None):
        logger.info("update called")
        print(pk)
        try:
            item = MenuItem.objects.get(id=pk)
        except MenuItem.DoesNotExist:
            return Response({
                "error": "Menu-Item not found"
            },status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(item,data=request.data,partial=True)
        logger.info("Serializer called")
        logger.info(serializer)
        serializer.is_valid(raise_exception=True)
        logger.info("validated")
        self.perform_update(serializer)
        return Response({
            "message" : "A Patch request"
        })

    def perform_update(self,serializer):
        logger.info("In perform update")
        
        instance = serializer.save()
        cache.delete(f'menuof__{instance.restaurant_id}')
        cache.delete(f'resto_{instance.restaurant_id}')
        logger.info(f"cache cleared after menu item update {instance.pk}")

    def perform_destroy(self,instance):
        resto_id = instance.restaurant_id
        instance.delete()
        cache.delete(f'menuof__{resto_id}')
        cache.delete(f'resto_{resto_id}')
        logger.info(f"cache cleared after menu item delete")
