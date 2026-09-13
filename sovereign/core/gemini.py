import json
import logging
import re

from django.conf import settings
from django.utils import timezone

from .models import FocusSession, Habit, JournalEntry, Todo

logger = logging.getLogger(__name__)


class GeminiAssistantError(Exception):
    pass


def _json_from_response(text):
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                pass
        raise GeminiAssistantError("Gemini returned an invalid response.") from exc


def build_context(user):
    today = timezone.localdate()
    habits = ", ".join(habit.name for habit in Habit.objects.filter(user=user)) or "none"
    todos = Todo.objects.filter(user=user, due_date__gte=today).values_list("title", "due_date", "completed")[:8]
    todo_summary = "; ".join(f"{title} ({due_date}, {'done' if completed else 'open'})" for title, due_date, completed in todos) or "none"
    journals = "; ".join(JournalEntry.objects.filter(user=user).values_list("title", flat=True)[:5]) or "none"
    focus_blocks = FocusSession.objects.filter(user=user, date=today).count()
    return f"Today is {today}. Habits: {habits}. Upcoming todos: {todo_summary}. Recent journal titles: {journals}. Focus blocks today: {focus_blocks}."


def ask_gemini(user, conversation_messages, message):
    normalized_message = message.lower()
    is_calendar_access_question = (
        "calendar" in normalized_message
        and any(term in normalized_message for term in ("access", "see", "view", "check", "read", "have"))
    )
    if is_calendar_access_question:
        return {
            "reply": (
                "I can access the todos in your Sovereign calendar, including their dates and completion status. "
                "I cannot access external calendars such as Google Calendar or Outlook."
            ),
            "action": None,
        }

    if not settings.GEMINI_API_KEY:
        raise GeminiAssistantError("Gemini is not configured yet. Add GEMINI_API_KEY to the environment and restart Django.")

    try:
        from google import genai
    except ImportError as exc:
        raise GeminiAssistantError("The Gemini SDK is not installed. Run pip install -r requirements.txt.") from exc

    history = "\n".join(f"{item.role}: {item.content}" for item in conversation_messages[-12:])
    prompt = f"""You are Sovereign, a concise and thoughtful personal growth assistant inside a habit, journal, todo, and focus app.
{build_context(user)}

Conversation:
{history}

New user message:
{message}

Return ONLY valid JSON with this shape. Set action to null unless the user clearly asks to create something:
{{
  "reply": "helpful response in plain text",
    "action": null
}}

For a create_todo action, use only: type, title, and due_date. The due_date must be YYYY-MM-DD.
For a create_habit action, use only: type, name, frequency, and target_count. Frequency must be daily or weekly.
For a create_journal action, use only: type, title, body, and mood. Mood must be an integer from 1 to 5.
For a set_focus_duration action, use only: type and duration_minutes. duration_minutes must be an integer from 5 to 120.
When the user asks to journal or save a reflection, create a concise descriptive title if they do not provide one.
Do not invent a due date; use today's date only when the user says today. Keep replies short, practical, and supportive."""
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
        except Exception as first_exc:
            first_error = str(first_exc).lower()
            fallback_error = any(
                marker in first_error
                for marker in ("404", "503", "unavailable", "high demand", "not found")
            )
            fallback_model = settings.GEMINI_FALLBACK_MODEL
            if fallback_model != settings.GEMINI_MODEL and fallback_error:
                response = client.models.generate_content(
                    model=fallback_model,
                    contents=prompt,
                    config={"response_mime_type": "application/json"},
                )
            else:
                raise
        data = _json_from_response(response.text or "")
    except GeminiAssistantError:
        raise
    except Exception as exc:
        logger.exception("Gemini request failed: %s", type(exc).__name__)
        error_text = str(exc).lower()
        if "401" in error_text or "403" in error_text or "api key" in error_text or "permission" in error_text:
            message = "Gemini rejected the API key. Create a new Gemini API key and replace GEMINI_API_KEY in .env."
        elif "429" in error_text or "quota" in error_text or "rate" in error_text:
            message = "Gemini rate limit or quota reached. Check the project quota and try again."
        elif "404" in error_text or "not found" in error_text:
            message = f"The Gemini model '{settings.GEMINI_MODEL}' is unavailable for this API key. Check GEMINI_MODEL."
        elif "503" in error_text or "unavailable" in error_text or "high demand" in error_text:
            message = "Gemini is temporarily busy. Please wait a moment and try again."
        else:
            message = "Gemini could not respond. Check the Django terminal for the provider error."
        raise GeminiAssistantError(message) from exc

    if not isinstance(data, dict) or not data.get("reply"):
        raise GeminiAssistantError("Gemini returned an incomplete response.")
    return data
