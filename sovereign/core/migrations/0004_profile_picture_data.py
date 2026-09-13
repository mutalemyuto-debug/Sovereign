from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_conversation_chatmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="profile_picture_content_type",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="profile",
            name="profile_picture_data",
            field=models.BinaryField(blank=True, null=True),
        ),
    ]