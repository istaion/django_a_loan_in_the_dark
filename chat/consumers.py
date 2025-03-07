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
        recipient_id = data.get('recipient_id', None)
        recipient = None
        
        if recipient_id:
            try:
                # Recherche par ID, pas par email
                recipient = await database_sync_to_async(CustomUser.objects.get)(id=recipient_id)
            except (CustomUser.DoesNotExist, ValueError):
                recipient = None
        
        message = await self.save_message(user, content, message_type, recipient)
        
        # Convertir UUID en chaîne de caractères
        recipient_id_str = str(recipient.id) if recipient else None
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': user.email,
                'message': message.content,
                'timestamp': message.formatted_timestamp,
                'message_type': message.message_type,
                'recipient_id': recipient_id_str,  # UUID converti en chaîne
                'is_staff': user.is_staff,
            }
        )

    async def chat_message(self, event):
        user = event['user']
        message = event['message']
        timestamp = event['timestamp']
        message_type = event['message_type']
        recipient_id = event['recipient_id']  # Maintenant c'est une chaîne
        is_staff = event.get('is_staff', False)
        
        if message_type == 'private':
            # Si l'utilisateur actuel est le staff ou le destinataire
            current_user_id = str(self.scope["user"].id)  # Convertir UUID en chaîne
            if self.scope["user"].is_staff or (recipient_id and current_user_id == recipient_id):
                await self.send(text_data=json.dumps(event))
        else:
            await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, content, message_type, recipient):
        return ChatMessage.objects.create(
            user=user, content=content, message_type=message_type, recipient=recipient
        )
