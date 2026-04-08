# Standard Library Imports
import logging
import json

# Third-Party Imports (Django)
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('main')

#==============================================================================
# 1. Customer Room
class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f'customer_{self.room_name}'  
        self.user = self.scope['user']
        if not self.user.utype == 'c' and str(self.user.id) != str(self.room_name):
            await self.close()
            return
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"connection started WITH {self.user} for ORDER {self.room_name} and group NAME : ---   {self.room_group_name} ")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data ):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
            }
        )

    async def chat_message(self,event):
        message = event["message"]
        print("inside the chat message function")
        await self.send(text_data=json.dumps({"message": message}))

#==============================================================================
# 2. Order Room
class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope["url_route"]["kwargs"])
        self.room_name = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = f'order_{self.room_name}'
        self.user = self.scope['user']
        print(self.user)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()



    async def disconnect(self, close_code):
        print(f"Connection closed with code: {close_code}")
        print(self.user)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data ):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("calling the chatmessage function")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
            }
        )

    async def chat_message(self,event):
        message = event["message"]
        print("inside the chat message function")
        print(message)
        
        await self.send(text_data=json.dumps({"message": message}))


    async def send_notification(self,event):
        notification = event['message']

        await self.send(text_data=json.dumps({
            'notification' : notification
        }))