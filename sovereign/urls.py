from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.static import serve

from sovereign.core import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("habits/add/", views.create_habit, name="create_habit"),
    path("habits/<int:habit_id>/toggle/", views.toggle_habit, name="toggle_habit"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("todos/add/", views.create_todo, name="create_todo"),
    path("todos/<int:todo_id>/toggle/", views.toggle_todo, name="toggle_todo"),
    path("focus/", views.focus_view, name="focus"),
    path("focus/complete/", views.complete_focus_session, name="complete_focus_session"),
    path("assistant/chat/", views.assistant_chat, name="assistant_chat"),
    path("assistant/history/", views.assistant_history, name="assistant_history"),
    path("journal/new/", views.create_journal_entry, name="create_journal"),
    path("journal/<int:entry_id>/", views.journal_detail, name="journal_detail"),
    path("profile/", views.update_profile, name="profile"),
    path("profile/picture/", views.profile_picture, name="profile_picture"),
]

urlpatterns += [
    path(
        "media/<path:path>",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
