from django.shortcuts import render
from django.http import Http404
from chat.models import ChatMessage

def chat_room(request, chat_type):
    # On vérifie si le type de chat est valide (général ou privé)
    if chat_type not in ['public', 'private']:
        raise Http404("Chat introuvable")

    # Si c'est un chat privé, on vérifie si l'utilisateur a des conversations privées existantes
    if chat_type == 'private':
        if request.user.is_staff:
            chat_messages = ChatMessage.objects.filter(message_type=chat_type).order_by('timestamp')
        else:
            chat_messages = ChatMessage.objects.filter(message_type=chat_type, recipient=request.user).order_by('timestamp')
    else:
        chat_messages = ChatMessage.objects.filter(message_type=chat_type).order_by('timestamp')

    return render(request, 'chat/chat_room.html', {
        'chat_type': chat_type,
        'user': request.user,
        'chat_messages': chat_messages
    })