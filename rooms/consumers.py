import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatMessage
from rooms.models import Room
from django.contrib.auth import get_user_model

User = get_user_model() 

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

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

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']
        username = user.username if user.is_authenticated else "Гость"

        await self.save_message(self.room_id, user if user.is_authenticated else None, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @sync_to_async
    def save_message(self, room_id, user, message):
        room = Room.objects.get(pk=room_id)
        if not user:
            try:
                user = User.objects.get(username='system')
            except User.DoesNotExist:
                user = None 
        ChatMessage.objects.create(
            room=room,
            user=user,
            message=message
        )
