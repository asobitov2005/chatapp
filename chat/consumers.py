import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_pk = self.scope['url_route']['kwargs']['room_pk']
        self.room_group_name = f'chat_{self.room_pk}'

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']

        # Save the message
        await self.save_message(sender_username, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_username
        }))

    @database_sync_to_async
    def save_message(self, sender_username, message):
        room = Room.objects.get(pk=self.room_pk)
        sender = User.objects.get(username=sender_username)
        Message.objects.create(room=room, sender=sender, message=message)
