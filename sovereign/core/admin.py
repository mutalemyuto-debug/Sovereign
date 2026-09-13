from django.contrib import admin

from .models import ChatMessage, Conversation, FocusSession, Goal, Habit, HabitLog, JournalEntry, Profile, Todo


admin.site.register([Profile, Habit, HabitLog, JournalEntry, Goal, Todo, FocusSession, Conversation, ChatMessage])
