from django.urls import re_path
from .import consumers

websocket_urlpatterns = [
    re_path(r'ws/whatsapp/(?P<branch_id>\d+)/branch/', consumers.WhatsappConsumer.as_asgi()),
]