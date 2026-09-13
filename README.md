# Sovereign

A focused self-improvement dashboard built with Django, HTML, CSS, and JavaScript.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ and create an account. Use `python manage.py createsuperuser` for the admin site.

## Gemini assistant

Create a new Gemini API key after rotating any key shared in chat, then create a `.env` file in the project root, next to `manage.py`:

```env
GEMINI_API_KEY=your-new-key
GEMINI_MODEL=gemini-3.6-flash
GEMINI_FALLBACK_MODEL=gemini-2.5-flash
```

Then run:

```powershell
python manage.py migrate
python manage.py runserver
```

The key is never stored in the database or frontend. The floating assistant can answer coaching questions and, when explicitly requested, create habits, todos, and journal entries for the signed-in user.
