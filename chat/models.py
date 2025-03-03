from django.db import models
from accounts.models import CustomUser
from django.db.models import Q

class ChatMessage(models.Model):

    PUBLIC = 'public'
    PRIVATE = 'private'

    MESSAGE_TYPES = [
        (PUBLIC,'Public'),
        (PRIVATE,'Private'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default=PUBLIC)
    
    # Pour les messages privés: à qui ce message est adressé
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE, 
        related_name='received_messages',
        null=True, 
        blank=True
    )

    # Pour le threading des réponses
    reply_to = models.ForeignKey(
        'self',
        on_delete = models.SET_NULL, 
        null=True,
        blank=True,
        related_name='replies' )
     
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        if self.message_type == self.PRIVATE:
            return f"[PRIVATE] {self.user.email} → {self.recipient.email if self.recipient else 'staff'}: {self.content[:30]}"
        return f"{self.user.email}: {self.content[:30]}"
    
    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime("%d-%m-%Y %H:%M")
    
    @property
    def is_staff(self):
        return self.user.is_staff