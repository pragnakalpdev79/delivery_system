# Standard Library Imports
import logging

# Third-Party Imports (Django)
from django.shortcuts import render
from django.contrib.auth.models import Group,Permission
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer,OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import generics,status,viewsets,filters
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports

from ....services.user_service import UserService
from ..serializers.auth import *

#============================================================
# 1.SIGNUP - Allowany
@extend_schema_view(
    create=extend_schema(
        summary=" U.1 Sign-Up",
        description=" Endpoint for new user registration of all types.",
        tags=["Userbase"],
        request=CustomUserRegistrationSerializer,
        responses=inline_serializer(
            name="Example Sign up successful",
            fields={
            'user' : serializers.EmailField(),
            'message' : serializers.CharField(),
            'refresh' : serializers.CharField(),
            'access' : serializers.CharField(),
        }
        ),
        examples=[
            OpenApiExample(
                "Example of Driver Registration Details Required",
                value={
                "username": "driver_123",
                "email": "driver123@example.com",
                "phone_number": "2971959499571",
                "password": "AstrongPassword123",
                "password_confirm": "AstrongPassword123",
                "first_name": "User_first_name",
                "last_name": "User_last_name",
                "utype": "d"
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Example of Customer Registration Details Required",
                value={
                "username": "customer_123",
                "email": "customer123@example.com",
                "phone_number": "2971959499572",
                "password": "AstrongPassword123",
                "password_confirm": "AstrongPassword123",
                "first_name": "User_first_name",
                "last_name": "User_last_name",
                "utype": "c"
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Example of Restaurant-owner Registration Details Required",
                value={
                "username": "restaurant_123",
                "email": "restaurant123@example.com",
                "phone_number": "2971959499571",
                "password": "AstrongPassword123",
                "password_confirm": "AstrongPassword123",
                "first_name": "User_first_name",
                "last_name": "User_last_name",
                "utype": "r"
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Example of Signup Success",
                value={
                    "user": "user@example.com",
                    "message" : "You have been successfully registered as a user",
                    'refresh' : "JWT REFRESH TOKEN",
                    'access' : "JWT ACCESS TOKEN",
                },
                request_only=False,
                response_only=True,
            ),
        ]
    ))
class UserRegistrationView(viewsets.ModelViewSet):
    serializer_class = CustomUserRegistrationSerializer
    http_method_names = ['post']
    permission_classes = [AllowAny]

    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cred = UserService.create_user(**serializer.validated_data)
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
    status = status.HTTP_200_OK

    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #NO service to be called here as serializer uses the authenticate function.
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
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({
                'error' : 'refresh_token is required'
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message' : 'Log out successful',
            },status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.info(f"An error occured in log out == {e}")
            return Response({
                'error' : 'Invalid or expired token'
            },status=status.HTTP_400_BAD_REQUEST)         
       

