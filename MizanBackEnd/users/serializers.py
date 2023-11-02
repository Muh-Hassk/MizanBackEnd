# serializers.py
from django.contrib.messages.storage.cookie import MessageSerializer
from rest_framework import serializers
from .models import User, Conversations, Messages, notCase


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'accountType']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)  # Include related messages

    class Meta:
        model = Conversations
        fields = '__all__'

class NotCaseSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)  # Include related messages
    class Meta:
        model = notCase
        fields = '__all__'

