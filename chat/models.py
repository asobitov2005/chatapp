from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_as_user2')

    def __str__(self):
        return f"{self.user1.username} and {self.user2.username}"

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self):
        return f"{self.sender.username} in {self.room}"
