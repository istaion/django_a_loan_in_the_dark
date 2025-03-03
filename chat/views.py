from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts import models
from .models import ChatMessage
from accounts.models import CustomUser
from django.db.models import Q

def chat_room(request):
    # Vérification supplémentaire (optionnelle car le middleware fait déjà cette vérification)
    if not request.session.get('token') or not request.session.get('user_info'):
        return redirect('/accounts/login/?next=' + request.path)
    
    # Récupère les 100 derniers messages
    public_messages = ChatMessage.objects.filter(message_type=ChatMessage.PUBLIC).order_by('-timestamp')[:100]
    #messages = reversed(messages)  # Inverser pour afficher les plus anciens d'abord
    
    user_id = request.session.get('user_info',{}).get('id')
    user = CustomUser.objects.get(id=user_id)

    if user.is_staff:
        # Pour le staff: tous les messages privés
        private_messages = ChatMessage.objects.filter(message_type=ChatMessage.PRIVATE).order_by('-timestamp')[:100]
    else:
        # Pour les utilisateurs: seulement leurs propres messages privés
        private_messages = ChatMessage.objects.filter(
            Q(user=user) | Q(recipient=user),
            message_type=ChatMessage.PRIVATE
        ).order_by('-timestamp')[:100]
    
    return render(request, 'chat/chat_room.html', {
        'public_messages': reversed(list(public_messages)),
        'private_messages': reversed(list(private_messages)),
        'user_info': request.session.get('user_info'),
        'settings': settings
    })
    

def message_list(request):
    # Vérification supplémentaire
    if not request.session.get('token') or not request.session.get('user_info'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    messages = ChatMessage.objects.filter(message_type=ChatMessage.PUBLIC).order_by('-timestamp')[:100]
    
    # Convertir les messages en liste de dictionnaires
    message_list = []
    for msg in reversed(list(messages)):
        message_list.append({
            'id': msg.id,
            'content': msg.content,
            'user_email': msg.user.email,
            'timestamp': msg.formatted_timestamp,
            'is_staff': msg.is_staff
        })
    
    return JsonResponse({'messages': message_list})

def private_message_list(request):
    if not request.session.get('token') or not request.session.get('user_info'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user_id = request.session.get('user_info', {}).get('id')
    user = CustomUser.objects.get(id=user_id)
    
    if user.is_staff:
        # Pour le staff: tous les messages privés
        messages = ChatMessage.objects.filter(message_type=ChatMessage.PRIVATE).order_by('-timestamp')[:100]
    else:
        # Pour les utilisateurs: seulement leurs propres messages privés
        messages = ChatMessage.objects.filter(
            Q(user=user) | Q(recipient=user),
            message_type = ChatMessage.PRIVATE
        ).order_by('-timestamp')[:100]
    
    # Convertir les messages en liste de dictionnaires
    message_list = []
    for msg in reversed(list(messages)):
        message_list.append({
            'id': msg.id,
            'content': msg.content,
            'user_email': msg.user.email,
            'recipient_email': msg.recipient.email if msg.recipient else None,
            'timestamp': msg.formatted_timestamp,
            'is_staff': msg.is_staff,
            'reply_to': msg.reply_to_id
        })
    return JsonResponse({'messages': message_list})


@require_POST
def send_message(request):
    # Vérification supplémentaire
    if not request.session.get('token') or not request.session.get('user_info'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    content = request.POST.get('content')
    if not content:
        return JsonResponse({'error': 'Message content is required'}, status=400)
    
    # Récupérer l'utilisateur actuel
    user_id = request.session.get('user_info', {}).get('id')
    if not user_id:
        return JsonResponse({'error': 'User not found'}, status=401)
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Créer le message
    message = ChatMessage.objects.create(
        user=user,
        content=content,
        message_type=ChatMessage.PUBLIC
    )
    
    # Diffuser le message via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_general",
        {
            'type': 'chat_message',
            'message': {
                'id': message.id,
                'content': message.content,
                'user_email': message.user.email,
                'timestamp': message.formatted_timestamp,
                'is_staff': message.is_staff
            }
        }
    )
    
    return JsonResponse({'status': 'success'})

@require_POST
def send_private_message(request):
    if not request.session.get('token') or not request.session.get('user_info'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    content = request.POST.get('content')
    recipient_id = request.POST.get('recipient_id')
    reply_to_id = request.POST.get('reply_to_id')
    
    if not content:
        return JsonResponse({'error': 'Message content is required'}, status=400)
    
    try:
        user = CustomUser.objects.get(id=request.session.get('user_info', {}).get('id'))
        
        # Vérifier si un destinataire a été spécifié
        recipient = None
        if recipient_id:
            recipient = CustomUser.objects.get(id=recipient_id)
        
        # Vérifier si c'est une réponse à un message existant
        reply_to = None
        if reply_to_id:
            reply_to = ChatMessage.objects.get(id=reply_to_id)
            
            # Si l'utilisateur répond à un message privé, utiliser le même destinataire
            if reply_to.message_type == ChatMessage.PRIVATE and not recipient:
                if reply_to.user == user:
                    recipient = reply_to.recipient
                else:
                    recipient = reply_to.user
        
        # Créer le message privé
        message = ChatMessage.objects.create(
            user=user,
            content=content,
            message_type=ChatMessage.PRIVATE,
            recipient=recipient,
            reply_to=reply_to
        )
        
        # Envoyer via WebSocket (si configuré)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "chat_private",
            {
                'type': 'private_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'user_email': message.user.email,
                    'recipient_email': message.recipient.email if message.recipient else None,
                    'timestamp': message.formatted_timestamp,
                    'is_staff': message.is_staff,
                    'reply_to': message.reply_to_id
                }
            }
        )
        
        return JsonResponse({'status': 'success', 'message_id': message.id})
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)