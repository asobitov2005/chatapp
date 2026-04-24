from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
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

        first_response = self.client.post(reverse("create_room", args=[self.bob.username]))
        room = Room.objects.get()

        self.assertRedirects(first_response, reverse("room", args=[room.pk]))
        self.assertEqual(Room.objects.count(), 1)

        second_response = self.client.post(reverse("create_room", args=[self.bob.username]))

        self.assertRedirects(second_response, reverse("room", args=[room.pk]))
        self.assertEqual(Room.objects.count(), 1)

    def test_create_room_requires_post(self):
        self.client.force_login(self.alice)

        response = self.client.get(reverse("create_room", args=[self.bob.username]))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(Room.objects.count(), 0)

    def test_room_pair_must_be_stored_in_order(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Room.objects.create(user1=self.bob, user2=self.alice)

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

    @patch("chat.api.views.async_to_sync")
    @patch("chat.api.views.get_channel_layer")
    def test_post_message_uses_authenticated_user_current_room_and_broadcasts(self, get_channel_layer, async_to_sync):
        channel_layer = Mock()
        sync_group_send = Mock()
        get_channel_layer.return_value = channel_layer
        async_to_sync.return_value = sync_group_send
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
        async_to_sync.assert_called_once_with(channel_layer.group_send)
        sync_group_send.assert_called_once_with(
            f"chat_{self.room.pk}",
            {
                "type": "chat_message",
                "message": "hello from alice",
                "sender": self.alice.username,
            },
        )

    def test_empty_message_is_rejected(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.post(
            reverse("message-list", args=[self.room.pk]),
            {"message": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Message.objects.count(), 0)
