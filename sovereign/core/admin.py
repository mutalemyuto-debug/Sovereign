from django.contrib import admin

from .models import FocusSession, Goal, Habit, HabitLog, JournalEntry, Profile, Todo


admin.site.register([Profile, Habit, HabitLog, JournalEntry, Goal, Todo, FocusSession])
