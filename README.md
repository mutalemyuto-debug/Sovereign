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
