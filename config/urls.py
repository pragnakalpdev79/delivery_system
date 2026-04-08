from django.contrib import admin
from django.urls import path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    #API V1
    path('api/v1/auth/',include('apps.users.api.v1.urls')),
    path('api/v1/restaurants/',include('apps.restaurants.api.v1.urls')),
    path('api/v1/cart/',include('apps.orders.api.v1.urls')),
    #API V2
    path('api/v2/restaurants/',include('apps.restaurants.api.v2.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),   
]
