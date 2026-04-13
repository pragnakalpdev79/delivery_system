import logging

from drf_spectacular.utils import extend_schema, extend_schema_view,inline_serializer,OpenApiExample
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ....selectors.profile_selector import ProfileSelector
from ....services.profile_service import ProfileService
from ..serializers.profile import CustomerProfileSerializerv, CustomProfileSerializer, DriverProfileSerializer,DriverProfileSerializeru
from ....permissions import IsCustomer,IsDriver

logger = logging.getLogger('main')

#============================================================
# 1. CUSTOMER PROFILE VIEW
@extend_schema_view(
    list=extend_schema(summary="P.1 Customer Profile",
                           description="Your profile details",
                            tags=["Customer-Profiles"],
                            responses=CustomerProfileSerializerv),
    partial_update=extend_schema(summary="P.2 Update Customer Profile", 
                                 description=" Update your profile details here",
                                 tags=["Customer-Profiles"],
                                 request=CustomProfileSerializer,
                                 responses=CustomProfileSerializer,
                                 ),
    retrieve=extend_schema(
        summary=" P.3 This method is not allowed",
        description = "Please use GET method instead",
        responses={
        405:{}},
        tags=["Customer-Profiles"]
    ),
)
class CustomerProfileView(viewsets.ModelViewSet):
    #DONE
    permission_classes = [IsCustomer]
    http_method_names=['get','patch']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return CustomProfileSerializer
        return CustomerProfileSerializerv


    def list(self, request):
        #DONE
        profile = ProfileSelector.get_user_profile(request.user)
        serializer = CustomerProfileSerializerv(profile)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        #DONE
        return Response({
            "error" : "Not Allowed",
        },status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, pk=None):
        #DONE USED ONLY TO UPDATE PROFILE AVATAR
        profile = ProfileSelector.get_user_profile(request.user)
        serializer = CustomProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = ProfileService.update_profile(request.user, **serializer.validated_data)
        if updated is None:
            return Response({"error": "profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CustomerProfileSerializerv(updated).data, status=status.HTTP_200_OK)

#============================================================
# 2. DRIVER PROFILE VIEW
@extend_schema_view(
    list=extend_schema(
        summary=" DP.1 Driver Profile",
        description="Your profile details",
        responses=DriverProfileSerializer,
        tags=["Driver-Profiles"]),
    partial_update=extend_schema(
        summary=" DP.2 Update Driver Profile",
        description=" Update your profile details here",
        request=DriverProfileSerializer,
        responses={
            404 
        },
        tags=['Driver-Profiles']
    ),
    retrieve=extend_schema(
        summary=" DP.3 This method is not allowed",
        description = "Please use GET method instead",
        tags=['Driver-Profiles'],
        responses={
            405:{}},
    ),
)
class DriverProfileView(viewsets.ModelViewSet):
    permission_classes = [IsDriver]
    http_method_names=['get','patch']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return DriverProfileSerializeru
        return DriverProfileSerializer


    def list(self, request):
        #DONE
        profile = ProfileSelector.get_driver_profile(request.user)
        return Response(DriverProfileSerializer(profile).data)

    def retrieve(self, request, *args, **kwargs):
        #DONE
        return Response({
            "error" : "Not Allowed",
        },status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, pk=None):
        #DONE
        profile = ProfileSelector.get_driver_profile(request.user)
        serializer = DriverProfileSerializeru(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = ProfileService.update_dprofile(request.user, **serializer.validated_data)
        if updated is None:
            return Response({"error": "profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DriverProfileSerializeru(updated).data, status=status.HTTP_200_OK)