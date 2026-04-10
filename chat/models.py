from django.db import models
from django.contrib.auth.models import User


def normalize_room_users(user_a, user_b):
    if user_a.pk == user_b.pk:
        raise ValueError("A private room requires two different users.")

    if user_a.pk < user_b.pk:
        return user_a, user_b
    return user_b, user_a


def get_or_create_private_room(user_a, user_b):
    first_user, second_user = normalize_room_users(user_a, user_b)
    room, _ = Room.objects.get_or_create(user1=first_user, user2=second_user)
    return room


class Room(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_as_user2')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user1=models.F("user2")),
                name="room_users_must_be_different",
            ),
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_private_room_pair",
            ),
        ]

    def __str__(self):
        return f"{self.user1.username} and {self.user2.username}"


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.sender.username} in {self.room}"
