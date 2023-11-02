from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    accountType = models.CharField(max_length=20)
    permissions = (("can_retrieve_conversations", "can retrieve conversations"),)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class Conversations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Messages(models.Model):
    role = models.CharField(max_length=10)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    Conversations = models.ForeignKey(Conversations, on_delete=models.CASCADE, related_name='messages_set')


class notCase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Conversations = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    message = models.TextField()