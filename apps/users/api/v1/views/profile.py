import logging

# Third-Party Imports (Django)
from django.shortcuts import render
from drf_spectacular.utils import extend_schema,extend_schema_view
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework import generics,status,viewsets,filters
from rest_framework.response import Response

# Local Imports
from ....selectors.profile_selector import ProfileSelector
from ....services.profile_service import ProfileService
from ..serializers.profile import *

#============================================================
# 1. CUSTOMER PROFILE VIEW
@extend_schema_view(
    retrieve=extend_schema(
        summary=" P.1 Customer Profile",
        description="Your profile details",
        tags=["Customer-Profiles"]),
    list=extend_schema(
        summary=" P.2 Not Allowed",
        description=" Please provide user id with get method",
        tags=['Customer-Profiles']
    ),
    partial_update=extend_schema(
        summary="P.3 Update Profile",
        description="Update your profile details here",
        tags=["Customer-Profiles"],
    )
)
class CustomerProfileView(viewsets.ModelViewSet):
    http_method_names = ["get","patch"]
    serializer_class = CustomProfileSerializer
    
    def list(self,request):
        return Response({
            "error" : "You can not list all profiles without admin access",
        })

    def retrieve(self,request,pk=None):
        logger.info(f"retrive called with pk= {pk}")
        logger.info(self.request.user)
        user = ProfileSelector.get_user_profile(self.request.user)
        logger.info(f"user:-- {user}")
        serializer = CustomerProfileSerializerv(user)
        logger.info(serializer)
        logger.info(serializer.data)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        print(user)
        print(self.request.data)
        profile = ProfileService.update_profile(user,**self.request.data)
        return Response(profile)

#============================================================
# 2. DRIVER PROFILE VIEW
@extend_schema_view(
    get=extend_schema(
        summary=" DP.1 Driver Profile",
        description="Your profile details",
        tags=["Driver-Profiles"]),
    patch=extend_schema(
        summary=" DP.2 Update Driver Profile",
        description=" Update your profile details here",
        tags=['Driver-Profiles']
    ),
    put=extend_schema(
        summary=" DP.3 This method is not allowed",
        description = "Please use patch method instead",
        tags=['Driver-Profiles']
    ),
)
class DriverProfileView(viewsets.ModelViewSet):
    http_method_names = ["get","patch"]
    serializer_class = DriverProfileSerializer

