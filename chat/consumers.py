from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.room_pk = self.scope['url_route']['kwargs']['room_pk']
        self.room_group_name = f'chat_{self.room_pk}'

        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.room = await self.get_room_for_user()
        if self.room is None:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message = (content.get("message") or "").strip()
        if not message:
            await self.send_json({"error": "Message cannot be empty."})
            return

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender']

        await self.send_json({
            'message': message,
            'sender': sender_username
        })

    @database_sync_to_async
    def get_room_for_user(self):
        return (
            Room.objects.filter(pk=self.room_pk)
            .filter(user1=self.user)
            .first()
            or Room.objects.filter(pk=self.room_pk, user2=self.user).first()
        )

    @database_sync_to_async
    def save_message(self, message):
        Message.objects.create(room=self.room, sender=self.user, message=message)
