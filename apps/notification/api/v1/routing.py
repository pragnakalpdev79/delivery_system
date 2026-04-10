from django.urls import re_path
from .consumers import OrderConsumer, CustomerConsumer,RestoConsumer

websocket_urlpatterns = [
    re_path(r'^ws/orders/(?P<order_id>[0-9a-f-]+)/$', OrderConsumer.as_asgi()),
    re_path(r'^ws/customer/(?P<user_id>[0-9a-f-]+)/$', CustomerConsumer.as_asgi()),
    re_path(r'^ws/restaurant/(?P<user_id>[0-9a-f-]+)/$', RestoConsumer.as_asgi()),

]

