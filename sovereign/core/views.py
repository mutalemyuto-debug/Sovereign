from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from calendar import monthrange
from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import HabitForm, JournalEntryForm, ProfileForm, SignupForm, TodoForm
from .gemini import GeminiAssistantError, ask_gemini
from .models import ChatMessage, Conversation, FocusSession, Habit, HabitLog, JournalEntry, Profile, Todo


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
    week_start = today - timedelta(days=(today.weekday() + 1) % 7)
    week_dates = [week_start + timedelta(days=index) for index in range(7)]
    history_start = week_start - timedelta(days=35)
    history_logs = {
        (log.habit_id, log.date): log.completed
        for log in HabitLog.objects.filter(
            habit__in=habits, date__gte=history_start, date__lte=week_dates[-1]
        )
    }
    today_logs = {
        log.habit_id: log
        for log in HabitLog.objects.filter(habit__in=habits, date=today)
    }
    for habit in habits:
        habit.today_log = today_logs.get(habit.id)
    habit_weeks = []
    for week_offset in range(5, -1, -1):
        start = week_start - timedelta(days=week_offset * 7)
        dates = [start + timedelta(days=index) for index in range(7)]
        habit_weeks.append({"dates": dates, "number": start.isocalendar().week, "is_current": start == week_start})
    habit_grid = [
        {
            "habit": habit,
            "weeks": [
                {
                    "dates": week["dates"],
                    "cells": [
                        history_logs.get((habit.id, day), False)
                        for day in week["dates"]
                    ],
                }
                for week in habit_weeks
            ],
        }
        for habit in habits
    ]
    habit_week_grids = [
        {
            "dates": week["dates"],
            "is_current": week["is_current"],
            "rows": [
                {
                    "habit": habit,
                    "cells": [
                        {
                            "date": day,
                            "completed": history_logs.get((habit.id, day), False),
                        }
                        for day in week["dates"]
                    ],
                }
                for habit in habits
            ],
        }
        for week in habit_weeks
    ]

    context = {
        "profile": profile,
        "habits": habits,
        "recent_entries": JournalEntry.objects.filter(user=request.user)[:5],
        "habit_form": HabitForm(),
        "journal_form": JournalEntryForm(),
        "today": today,
        "week_dates": week_dates,
        "habit_weeks": habit_weeks,
        "history_logs": history_logs,
        "habit_grid": habit_grid,
        "habit_week_grids": habit_week_grids,
        "has_habit_history": len(habit_week_grids) > 1,
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
def calendar_view(request):
    today = timezone.localdate()
    try:
        selected = datetime.strptime(request.GET.get("month", ""), "%Y-%m").date().replace(day=1)
    except ValueError:
        selected = today.replace(day=1)
    previous_month = (selected - timedelta(days=1)).replace(day=1)
    next_month = (selected + timedelta(days=monthrange(selected.year, selected.month)[1])).replace(day=1)
    first_day = selected - timedelta(days=(selected.weekday() + 1) % 7)
    calendar_days = [first_day + timedelta(days=index) for index in range(42)]
    todos = Todo.objects.filter(user=request.user, due_date__gte=calendar_days[0], due_date__lte=calendar_days[-1])
    todos_by_date = {}
    for todo in todos:
        todos_by_date.setdefault(todo.due_date, []).append(todo)
    calendar_cells = [
        {"day": day, "todos": todos_by_date.get(day, [])}
        for day in calendar_days
    ]
    return render(request, "calendar.html", {
        "selected_month": selected,
        "calendar_days": calendar_days,
        "calendar_cells": calendar_cells,
        "upcoming_todos": [todo for todo in todos if not todo.completed],
        "previous_month": previous_month,
        "next_month": next_month,
        "today": today,
        "todo_form": TodoForm(initial={"due_date": today}),
    })


@login_required
@require_POST
def create_todo(request):
    form = TodoForm(request.POST)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        todo.save()
        messages.success(request, "Todo added.")
    return redirect(f"/calendar/?month={request.POST.get('due_date', '')[:7]}")


@login_required
@require_POST
def toggle_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.completed = not todo.completed
    todo.save(update_fields=["completed"])
    return JsonResponse({"completed": todo.completed, "todo_id": todo.id})


@login_required
def focus_view(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    sessions = FocusSession.objects.filter(user=request.user, date__gte=month_start, date__lte=today)
    daily_sessions = {}
    for session in sessions:
        daily_sessions.setdefault(session.date, []).append(session)
    return render(request, "focus.html", {
        "profile": Profile.objects.get_or_create(user=request.user)[0],
        "today": today,
        "today_sessions": daily_sessions.get(today, []),
        "today_minutes": sum(session.duration_minutes for session in daily_sessions.get(today, [])),
        "month_sessions": sessions,
        "month_minutes": sum(session.duration_minutes for session in sessions),
        "month_blocks": sessions.count(),
        "daily_sessions": daily_sessions,
    })


@login_required
@require_POST
def complete_focus_session(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    FocusSession.objects.create(
        user=request.user,
        date=timezone.localdate(),
        duration_minutes=profile.focus_duration,
    )
    return JsonResponse({"blocks": FocusSession.objects.filter(user=request.user, date=timezone.localdate()).count()})


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


@login_required
@require_POST
def assistant_chat(request):
    message = request.POST.get("message", "").strip()
    if not message or len(message) > 2000:
        return JsonResponse({"error": "Please enter a message up to 2,000 characters."}, status=400)

    conversation_id = request.POST.get("conversation_id")
    conversation = Conversation.objects.filter(id=conversation_id, user=request.user).first() if conversation_id else None
    if conversation is None:
        conversation = Conversation.objects.create(user=request.user)

    previous_messages = list(conversation.messages.all())
    user_message = ChatMessage.objects.create(
        conversation=conversation, role=ChatMessage.Role.USER, content=message
    )
    try:
        result = ask_gemini(request.user, previous_messages, message)
        action_message = apply_assistant_action(request.user, result.get("action"))
        reply = result["reply"]
        if action_message:
            reply = f"{reply}\n\n{action_message}"
    except GeminiAssistantError as exc:
        user_message.delete()
        return JsonResponse({"error": str(exc)}, status=503)

    ChatMessage.objects.create(
        conversation=conversation, role=ChatMessage.Role.ASSISTANT, content=reply
    )
    return JsonResponse({"conversation_id": conversation.id, "reply": reply})


def apply_assistant_action(user, action):
    if not isinstance(action, dict):
        return ""
    action_type = action.get("type")
    if action_type == "create_todo":
        title = str(action.get("title", "")).strip()[:180]
        due_date = action.get("due_date")
        try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return "I did not create the todo because the date was unclear."
        if title:
            Todo.objects.create(user=user, title=title, due_date=due_date)
            return f"Added todo: {title} for {due_date.strftime('%b %d').lstrip('0')}."
    elif action_type == "create_habit":
        name = str(action.get("name", "")).strip()[:120]
        frequency = action.get("frequency", Habit.Frequency.DAILY)
        if name and frequency in Habit.Frequency.values:
            try:
                target_count = max(1, min(int(action.get("target_count", 1)), 20))
            except (TypeError, ValueError):
                target_count = 1
            Habit.objects.create(
                user=user,
                name=name,
                frequency=frequency,
                target_count=target_count,
            )
            return f"Added habit: {name}."
    elif action_type == "create_journal":
        title = str(action.get("title", "Reflection")).strip()[:160]
        body = str(action.get("body", "")).strip()
        try:
            mood = max(1, min(int(action.get("mood", 3)), 5))
        except (TypeError, ValueError):
            mood = 3
        if body:
            JournalEntry.objects.create(user=user, title=title or "Reflection", body=body, mood=mood)
            return "Saved that reflection to your journal."
    return ""