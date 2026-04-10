from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from chat.models import Message, Room


class RoomFlowTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="StrongPass123!")
        self.bob = User.objects.create_user(username="bob", password="StrongPass123!")

    def test_create_room_redirects_to_private_room_and_reuses_existing_room(self):
        self.client.force_login(self.alice)

        first_response = self.client.get(reverse("create_room", args=[self.bob.username]))
        room = Room.objects.get()

        self.assertRedirects(first_response, reverse("room", args=[room.pk]))
        self.assertEqual(Room.objects.count(), 1)

        second_response = self.client.get(reverse("create_room", args=[self.bob.username]))

        self.assertRedirects(second_response, reverse("room", args=[room.pk]))
        self.assertEqual(Room.objects.count(), 1)

    def test_non_member_cannot_open_room_page(self):
        charlie = User.objects.create_user(username="charlie", password="StrongPass123!")
        room = Room.objects.create(user1=self.alice, user2=self.bob)

        self.client.force_login(charlie)
        response = self.client.get(reverse("room", args=[room.pk]))

        self.assertEqual(response.status_code, 403)


class MessageApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", password="StrongPass123!")
        self.bob = User.objects.create_user(username="bob", password="StrongPass123!")
        self.charlie = User.objects.create_user(username="charlie", password="StrongPass123!")
        self.room = Room.objects.create(user1=self.alice, user2=self.bob)

    def test_room_messages_are_hidden_from_non_members(self):
        Message.objects.create(room=self.room, sender=self.alice, message="Secret")
        self.client.force_authenticate(user=self.charlie)

        response = self.client.get(reverse("message-list", args=[self.room.pk]))

        self.assertEqual(response.status_code, 403)

    def test_post_message_uses_authenticated_user_and_current_room(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.post(
            reverse("message-list", args=[self.room.pk]),
            {"message": "  hello from alice  ", "sender": "bob", "room": 999},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)

        message = Message.objects.get()
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.alice)
        self.assertEqual(message.message, "hello from alice")

    def test_empty_message_is_rejected(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.post(
            reverse("message-list", args=[self.room.pk]),
            {"message": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Message.objects.count(), 0)
