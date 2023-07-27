import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from accounts.models import CustomUser


class WhatsappConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.branch_id = self.scope['url_route']['kwargs']['branch_id']
        self.room_group_name = f'whatsapp_socket_{self.branch_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # receive message from room group
    async def whatsapp_socket(self, event):
        await self.send(text_data=json.dumps(event))