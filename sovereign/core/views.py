from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import HabitForm, JournalEntryForm, ProfileForm, SignupForm
from .models import Habit, HabitLog, JournalEntry, Profile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user)
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "registration/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    today = timezone.localdate()
    profile, _ = Profile.objects.get_or_create(user=request.user)
    habits = list(Habit.objects.filter(user=request.user))
    today_logs = {
        log.habit_id: log
        for log in HabitLog.objects.filter(habit__in=habits, date=today)
    }
    for habit in habits:
        habit.today_log = today_logs.get(habit.id)

    context = {
        "profile": profile,
        "habits": habits,
        "recent_entries": JournalEntry.objects.filter(user=request.user)[:5],
        "habit_form": HabitForm(),
        "journal_form": JournalEntryForm(),
        "today": today,
    }
    return render(request, "dashboard.html", context)


@login_required
@require_POST
def toggle_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    log, _ = HabitLog.objects.get_or_create(habit=habit, date=timezone.localdate())
    log.completed = not log.completed
    log.save(update_fields=["completed"])
    return JsonResponse({"completed": log.completed, "habit_id": habit.id})


@login_required
@require_POST
def create_habit(request):
    form = HabitForm(request.POST)
    if form.is_valid():
        habit = form.save(commit=False)
        habit.user = request.user
        habit.save()
        messages.success(request, "Habit added.")
    return redirect("dashboard")


@login_required
def create_journal_entry(request):
    form = JournalEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
        messages.success(request, "Journal entry saved.")
        return redirect("dashboard")
    return render(request, "journal_form.html", {"form": form})


@login_required
def update_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("dashboard")
    return render(request, "profile_form.html", {"form": form, "profile": profile})