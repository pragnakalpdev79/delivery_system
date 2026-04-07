# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.shortcuts import render
from django.contrib.auth.models import Group,Permission
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import generics,status,viewsets,filters
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports

from ....services.user_service import UserService
from ..serializers.auth import *

@extend_schema_view(
    create=extend_schema(
        summary=" U.1 Sign-Up",
        description=" Endpoint for new user registration of all types.",
        tags=["Userbase"],
    ))
class UserRegistrationView(viewsets.ModelViewSet):
    serializer_class = CustomUserRegistrationSerializer
    http_method_names = ['post']
    permission_classes = [AllowAny]

    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cred = UserService.create_user(**serializer.data)
        return Response(cred,status=status.HTTP_201_CREATED)
    
    
#============================================================
# 2.LOGIN - Allowany
@extend_schema_view(
    create=extend_schema(
        summary=" U.2 Login",
        description="Registered users login here",
        tags=["Userbase"],
    ))
class UserLoginView(viewsets.ModelViewSet):
    http_method_names = ['post']
    permission_classes = [AllowAny]
    serializer_class = CustomUserLoginSerializer

    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = RefreshToken.for_user(serializer.validated_data['user'])
        return Response({
            'user' : serializer.validated_data['email'],
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        },status=status.HTTP_200_OK)


#============================================================
# 3.LOGOUT - Logged in user only
@extend_schema_view(
    create=extend_schema(
        summary=" U.3 Logout",
        description="Logged-in users logout here",
        tags=["Userbase"],
    ))
class UserLogoutView(viewsets.ModelViewSet):
    permission_classes =  [IsAuthenticated]
    http_method_names = ['post']

    def create(self,request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        
            return Response({
                'message' : 'Log out successful',
            },status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            logger.info(f"An error occured in log out == {e}")
            return Response({
                'error' : 'something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)         

