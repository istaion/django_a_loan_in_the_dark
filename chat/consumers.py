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
        
        # Obtenir l'URL de l'avatar
        avatar_url = await self.get_avatar_url(user)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': user.email,
                'user_id': str(user.id),
                'message': message.content,
                'timestamp': message.formatted_timestamp,
                'message_type': message.message_type,
                'recipient_id': str(recipient.id) if recipient else None,
                'is_staff': user.is_staff,
                'avatar_url': avatar_url,
            }
        )
        
    async def chat_message(self, event):
        user = event['user']
        message = event['message']
        timestamp = event['timestamp']
        message_type = event['message_type']
        recipient_id = event['recipient_id']
        is_staff = event.get('is_staff', False)
        avatar_url = event.get('avatar_url', None)
        
        if message_type == 'private':
            # Si l'utilisateur actuel est le staff ou le destinataire
            current_user_id = str(self.scope["user"].id)
            if self.scope["user"].is_staff or (recipient_id and current_user_id == recipient_id):
                await self.send(text_data=json.dumps(event))
        else:
            await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def save_message(self, user, content, message_type, recipient):
        return ChatMessage.objects.create(
            user=user, content=content, message_type=message_type, recipient=recipient
        )
    
    @database_sync_to_async
    def get_avatar_url(self, user):
        if user.profile_picture:
            return user.profile_picture.url
        return None  # Retourne None pour utiliser l'avatar par défaut dans le frontend