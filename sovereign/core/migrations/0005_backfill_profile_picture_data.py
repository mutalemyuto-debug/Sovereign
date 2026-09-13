from django.conf import settings
from django.db import migrations


def copy_existing_profile_pictures(apps, schema_editor):
    Profile = apps.get_model("core", "Profile")
    for profile in Profile.objects.exclude(profile_picture=""):
        if profile.profile_picture_data:
            continue
        try:
            with profile.profile_picture.storage.open(profile.profile_picture.name, "rb") as image_file:
                profile.profile_picture_data = image_file.read()
        except (FileNotFoundError, OSError):
            continue
        profile.profile_picture_content_type = "image/jpeg"
        profile.save(update_fields=["profile_picture_data", "profile_picture_content_type"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_profile_picture_data"),
    ]

    operations = [
        migrations.RunPython(copy_existing_profile_pictures, migrations.RunPython.noop),
    ]
