from django.db import migrations, models


def order_private_rooms(apps, schema_editor):
    Room = apps.get_model("chat", "Room")
    Message = apps.get_model("chat", "Message")

    for room in Room.objects.all().order_by("id"):
        if room.user1_id < room.user2_id:
            continue

        duplicate = (
            Room.objects.filter(user1_id=room.user2_id, user2_id=room.user1_id)
            .exclude(pk=room.pk)
            .first()
        )
        if duplicate:
            Message.objects.filter(room_id=room.pk).update(room_id=duplicate.pk)
            room.delete()
            continue

        room.user1_id, room.user2_id = room.user2_id, room.user1_id
        room.save(update_fields=["user1", "user2"])


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0002_room_constraints"),
    ]

    operations = [
        migrations.RunPython(order_private_rooms, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="room",
            constraint=models.CheckConstraint(
                condition=models.Q(user1__lt=models.F("user2")),
                name="room_users_must_be_ordered",
            ),
        ),
    ]
