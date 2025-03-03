from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
import os

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    api_token = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='accounts', null=True, blank=True)
    phone_number = models.CharField(max_length=55, null=True, blank=True)
    advisor =  models.ManyToManyField("self", symmetrical=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'custom_user'

    def __repr__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.profile_picture:  
            self.profile_picture.name = os.path.join(MEDIA_DIR, 'default-avatar.jpg')
        
        super().save(*args, **kwargs)

