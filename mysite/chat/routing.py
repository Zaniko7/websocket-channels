from django.urls import path

from chat import consumers

websocket_urlpatterns = [
    path('ws/', consumers.EchoConsumer.as_asgi()),
    path('ws/chat/<str:username>/', consumers.ChatConsumer.as_asgi()),
]