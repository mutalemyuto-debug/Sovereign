from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="focus_duration",
            field=models.PositiveSmallIntegerField(default=25, validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(120)]),
        ),
        migrations.CreateModel(
            name="Todo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("due_date", models.DateField()),
                ("completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="todos", to="auth.user")),
            ],
            options={"ordering": ["completed", "due_date", "created_at"]},
        ),
        migrations.CreateModel(
            name="FocusSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("duration_minutes", models.PositiveSmallIntegerField()),
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="focus_sessions", to="auth.user")),
            ],
            options={"ordering": ["-completed_at"]},
        ),
    ]
