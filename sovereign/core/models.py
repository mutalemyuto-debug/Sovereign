from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    focus_duration = models.PositiveSmallIntegerField(
        default=25, validators=[MinValueValidator(5), MaxValueValidator(120)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Habit(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=120)
    frequency = models.CharField(
        max_length=20, choices=Frequency.choices, default=Frequency.DAILY
    )
    target_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["habit", "date"], name="unique_habit_log_per_day"
            )
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.habit.name} - {self.date}"


class JournalEntry(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="journal_entries"
    )
    title = models.CharField(max_length=160)
    body = models.TextField()
    mood = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=180)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["completed", "due_date", "created_at"]

    def __str__(self):
        return self.title


class FocusSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="focus_sessions")
    date = models.DateField()
    duration_minutes = models.PositiveSmallIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.duration_minutes} min)"


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=120, default="Sovereign assistant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=160)
    target_date = models.DateField()
    progress = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["target_date", "title"]

    def __str__(self):
        return self.title