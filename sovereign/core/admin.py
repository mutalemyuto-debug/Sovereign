from django.contrib import admin

from .models import Goal, Habit, HabitLog, JournalEntry, Profile


admin.site.register([Profile, Habit, HabitLog, JournalEntry, Goal])
