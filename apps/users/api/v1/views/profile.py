import logging

# Third-Party Imports (Django)
from django.shortcuts import render
from drf_spectacular.utils import extend_schema,extend_schema_view
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework import generics,status,viewsets,filters
from rest_framework.response import Response

# Local Imports
from ....selectors.profile_selector import ProfileSelector


class CustomerProfileView(viewsets.ModelViewSet):
    http_method_names = ["get","patch"]
    serializer_class = CUstomerProfileSerializer
    
    def retrieve(self,request,pk=None):
        user = ProfileSelector.get_user_profile(self.request.user)
