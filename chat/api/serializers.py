from rest_framework import serializers
from django.contrib.auth.models import User
from chat.models import Room, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RoomSerializer(serializers.ModelSerializer):
    user1 = UserSerializer()
    user2 = UserSerializer()

    class Meta:
        model = Room
        fields = ['id', 'user1', 'user2']


class MessageSerializer(serializers.ModelSerializer):
    room = RoomSerializer()

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'message']
