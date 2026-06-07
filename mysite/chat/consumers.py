import json

from channels.generic.websocket import WebsocketConsumer
# from channels.consumer import SyncConsumer

# class EchoConsumer(SyncConsumer):

#     def websocket_connect(self, event):
#         self.send({
#             "type": "websocket.accept",
#         })

#     def websocket_receive(self, event):
#         self.send({
#             "type": "websocket.send",
#             "text": event["text"],
#         })

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
import json

class EchoConsumer(WebsocketConsumer):
    def connect(self):

        self.accept()
        
    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            self.send(text_data=text_data + " - Sent By Server")
        elif bytes_data:
            self.send(bytes_data=bytes_data)

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['username']
        self.group_name = f"chat_{self.user_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            username = text_data_json['receiver']
            user_group_name = f"chat_{username}"
            
            async_to_sync(self.channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'chat_message',
                    'message': text_data
                }
            )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=message)
