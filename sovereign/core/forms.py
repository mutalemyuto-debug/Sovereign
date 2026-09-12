from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Habit, JournalEntry, Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "profile_picture")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ("name", "frequency", "target_count")


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ("title", "body", "mood")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),
            "mood": forms.NumberInput(attrs={"min": 1, "max": 5}),
        }