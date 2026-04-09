from django.contrib import admin
from django.urls import path, include
from config import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API V1
    path('api/v1/auth/', include('apps.users.api.v1.urls')),
    path('api/v1/restaurants/', include('apps.restaurants.api.v1.urls')),
    path('api/v1/orders/', include('apps.orders.api.v1.urls')),

    # API V2
    path('api/v2/restaurants/', include('apps.restaurants.api.v2.urls')),

    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.base.STATIC_URL, document_root=settings.base.STATIC_ROOT)