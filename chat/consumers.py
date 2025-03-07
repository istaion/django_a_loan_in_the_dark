import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .models import ChatMessage
from accounts.models import CustomUser

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_type = self.scope['url_route']['kwargs']['chat_type']
        self.room_group_name = f'chat_{self.chat_type}'

        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]
        content = data['message']
        message_type = data.get('type', 'public')
        recipient_email = data.get('recipient', None)

        recipient = None
        if recipient_email:
            try:
                recipient = await database_sync_to_async(CustomUser.objects.get)(email=recipient_email)
            except CustomUser.DoesNotExist:
                recipient = None
                
        message = await self.save_message(user, content, message_type, recipient)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': user.email,
                'message': message.content,
                'timestamp': message.formatted_timestamp,
                'message_type': message.message_type,
                'recipient': recipient.email if recipient else None,
            }
        )

    async def chat_message(self, event):
        user = event['user']
        message = event['message']
        timestamp = event['timestamp']
        message_type = event['message_type']
        recipient = event['recipient']

        if message_type == 'private':
            if self.scope["user"].is_staff or self.scope["user"].email == recipient:
                await self.send(text_data=json.dumps(event))
        else:
            await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, content, message_type, recipient):
        return ChatMessage.objects.create(
            user=user, content=content, message_type=message_type, recipient=recipient
        )
