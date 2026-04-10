from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="room",
            constraint=models.CheckConstraint(
                check=~models.Q(user1=models.F("user2")),
                name="room_users_must_be_different",
            ),
        ),
        migrations.AddConstraint(
            model_name="room",
            constraint=models.UniqueConstraint(
                fields=("user1", "user2"),
                name="unique_private_room_pair",
            ),
        ),
    ]
