from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room, name='chat_room'),
    path('api/messages/', views.message_list, name='message_list'),
    path('api/send/', views.send_message, name='send_message'),
    path('send/', views.send_message, name='send_message'),
    path('messages/', views.message_list, name='message_list'),
    path('api/private/messages/', views.private_message_list, name='api_private_message_list'),
    path('api/private/send/', views.send_private_message, name='send_private_message'),
]
