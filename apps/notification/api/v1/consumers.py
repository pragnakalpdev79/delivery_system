# Standard Library Imports
import logging
import json

# Third-Party Imports (Django)
from channels.generic.websocket import AsyncWebsocketConsumer
from drf_spectacular_websocket.decorators import extend_ws_schema

logger = logging.getLogger('main')


#==============================================================================
# 1. Customer Room
class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f'customer_{self.room_name}'
        self.user = self.scope.get('user')
        print("trying to connect")

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        if self.user.utype != 'c' or str(self.user.id) != str(self.room_name):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        logger.info(f"customer ws connected -- user {self.user.id} room {self.room_group_name}")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    extend_ws_schema(
        type='send',
        summary='test'
    )
    async def receive(self, text_data):
        payload = json.loads(text_data)
        message = payload.get("message", "")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            }
        )
    async def send_notification(self, event):
        logger.info(f" sending -- {event["message"]}")
        await self.send(text_data=json.dumps({"notification": event["message"]}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))


#==============================================================================
# 2. Order Room
class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = f'order_{self.room_name}'
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        logger.info(f"order ws connected -- user {self.user.id} room {self.room_group_name}")
        await self.accept()

    async def disconnect(self, close_code):
        logger.info("disconnecting")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        message = payload.get("message", "")
        logger.info(f" rec msg -- {message}")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            }
        )
    async def send_notification(self, event):
        logger.info(f" sending -- {event["message"]}")
        await self.send(text_data=json.dumps({"notification": event["message"]}))

#==============================================================================
# 2. Restaurant Room
class RestoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = f'restaurant_{self.room_name}'
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated and not self.user.utype == 'r' :
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        logger.info(f"resto ws connected -- owner {self.user.id} room {self.room_group_name}")
        await self.accept()

    async def disconnect(self, close_code):
        logger.info("disconnecting")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        message = payload.get("message", "")
        logger.info(f" rec msg -- {message}")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            }
        )
    async def send_notification(self, event):
        logger.info(f" sending -- {event["message"]}")
        await self.send(text_data=json.dumps({"notification": event["message"]}))
