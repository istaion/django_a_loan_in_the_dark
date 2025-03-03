# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import CustomUser
from .models import ChatMessage
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Rejoindre les deux groupes de chat
        await self.channel_layer.group_add("chat_general", self.channel_name)
        await self.channel_layer.group_add("chat_private", self.channel_name)
        
        await self.accept()
        
        # Si l'utilisateur est authentifié, envoyer un message de connexion
        if self.scope.get('user') and self.scope['user'].is_authenticated:
            user_email = self.scope['user'].email
            await self.channel_layer.group_send(
                "chat_general",
                {
                    'type': 'user_join',
                    'user': user_email
                }
            )
    
    async def disconnect(self, close_code):
        # Quitter les deux groupes de chat
        await self.channel_layer.group_discard("chat_general", self.channel_name)
        await self.channel_layer.group_discard("chat_private", self.channel_name)
        
        # Si l'utilisateur est authentifié, envoyer un message de déconnexion
        if self.scope.get('user') and self.scope['user'].is_authenticated:
            user_email = self.scope['user'].email
            await self.channel_layer.group_send(
                "chat_general",
                {
                    'type': 'user_leave',
                    'user': user_email
                }
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if not self.scope.get('user') or not self.scope['user'].is_authenticated:
            return
            
        user = self.scope['user']
        
        if message_type == 'private_message':
            # Traiter un message privé
            content = data.get('message')
            recipient_id = data.get('recipient_id')
            reply_to_id = data.get('reply_to_id')
            
            # Créer et diffuser le message privé
            message_id = await self.save_private_message(user, content, recipient_id, reply_to_id)
            
            await self.channel_layer.group_send(
                "chat_private",
                {
                    'type': 'private_message',
                    'message': {
                        'id': message_id,
                        'content': content,
                        'user_email': user.email,
                        'user_id': str(user.id),
                        'recipient_id': recipient_id,
                        'timestamp': timezone.now().strftime('%d-%m-%Y %H:%M'),
                        'is_staff': user.is_staff,
                        'reply_to': reply_to_id
                    }
                }
            )
        else:
            # Message public standard
            message = data.get('message')
            if message:
                message_id = await self.save_message(user, message)
                
                await self.channel_layer.group_send(
                    "chat_general",
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': message_id,
                            'content': message,
                            'user_email': user.email,
                            'timestamp': timezone.now().strftime('%d-%m-%Y %H:%M'),
                            'is_staff': user.is_staff
                        }
                    }
                )
    
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))
    
    async def private_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'private_message',
            'message': message
        }))
    
    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user': event['user']
        }))
    
    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user': event['user']
        }))
    
    @database_sync_to_async
    def save_message(self, user, content):
        message = ChatMessage.objects.create(
            user=user,
            content=content,
            message_type='public'
        )
        return message.id
        
    @database_sync_to_async
    def save_private_message(self, user, content, recipient_id=None, reply_to_id=None):
        recipient = None
        if recipient_id:
            try:
                recipient = CustomUser.objects.get(id=recipient_id)
            except CustomUser.DoesNotExist:
                pass
                
        reply_to = None
        if reply_to_id:
            try:
                reply_to = ChatMessage.objects.get(id=reply_to_id)
            except ChatMessage.DoesNotExist:
                pass
                
        message = ChatMessage.objects.create(
            user=user,
            content=content,
            message_type='private',
            recipient=recipient,
            reply_to=reply_to
        )
        return message.id