(() => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    document.querySelectorAll('.nav-dropdown').forEach((dropdown) => {
        dropdown.removeAttribute('open');
    });

    document.addEventListener('click', (event) => {
        document.querySelectorAll('.nav-dropdown[open]').forEach((dropdown) => {
            if (!dropdown.contains(event.target)) dropdown.removeAttribute('open');
        });
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            document.querySelectorAll('.nav-dropdown[open]').forEach((dropdown) => dropdown.removeAttribute('open'));
        }
    });

    document.querySelectorAll('.flash-message').forEach((message) => {
        window.setTimeout(() => message.classList.add('is-hidden'), 3000);
    });

    const assistant = document.querySelector('[data-assistant-widget]');
    if (assistant) {
        const toggles = assistant.querySelectorAll('[data-assistant-toggle]');
        const panel = assistant.querySelector('.assistant-panel');
        const form = assistant.querySelector('[data-assistant-form]');
        const messages = assistant.querySelector('[data-assistant-messages]');
        let conversationId = null;
        toggles.forEach((toggle) => toggle.addEventListener('click', () => {
            const isOpening = panel.hidden;
            panel.hidden = !isOpening;
            toggles.forEach((button) => button.setAttribute('aria-expanded', String(isOpening)));
            if (isOpening) form.querySelector('textarea').focus();
        }));
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const textarea = form.querySelector('textarea');
            const sendButton = form.querySelector('button[type="submit"]');
            const message = textarea.value.trim();
            if (!message) return;
            const userBubble = document.createElement('div');
            userBubble.className = 'assistant-message assistant-message-user';
            userBubble.textContent = message;
            messages.appendChild(userBubble);
            textarea.value = '';
            sendButton.disabled = true;
            const typingBubble = document.createElement('div');
            typingBubble.className = 'assistant-message assistant-message-bot assistant-typing';
            typingBubble.setAttribute('role', 'status');
            typingBubble.setAttribute('aria-label', 'Sovereign is typing');
            typingBubble.innerHTML = '<span class="assistant-typing-spark" aria-hidden="true">✦</span>';
            messages.appendChild(typingBubble);
            messages.scrollTop = messages.scrollHeight;
            const body = new URLSearchParams({ message });
            if (conversationId) body.set('conversation_id', conversationId);
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded' },
                    body,
                });
                const data = await response.json();
                typingBubble.remove();
                const bubble = document.createElement('div');
                bubble.className = 'assistant-message assistant-message-bot';
                bubble.textContent = response.ok ? data.reply : data.error;
                messages.appendChild(bubble);
                if (response.ok) conversationId = data.conversation_id;
            } catch (error) {
                typingBubble.remove();
                const bubble = document.createElement('div');
                bubble.className = 'assistant-message assistant-message-bot';
                bubble.textContent = 'I could not connect right now. Please try again.';
                messages.appendChild(bubble);
            } finally {
                sendButton.disabled = false;
                messages.scrollTop = messages.scrollHeight;
            }
        });
    }

    document.querySelectorAll('[data-history-toggle]').forEach((button) => {
        button.addEventListener('click', () => {
            const card = button.previousElementSibling;
            const expanded = !card.classList.contains('show-history');
            card.classList.toggle('show-history', expanded);
            card.querySelectorAll('.history-week').forEach((week) => { week.hidden = !expanded; });
            button.setAttribute('aria-expanded', expanded);
            button.firstChild.textContent = expanded ? 'Hide past weeks ' : 'View full history ';
            button.querySelector('span').textContent = expanded ? '↑' : '→';
        });
    });

    document.querySelectorAll('[data-habit-toggle]').forEach((button) => {
        button.addEventListener('click', async () => {
            button.disabled = true;
            const row = button.closest('[data-habit-id]');
            const status = row?.querySelector('.habit-status');
            try {
                const response = await fetch(button.dataset.habitToggle, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
                });
                if (!response.ok) throw new Error('Habit update failed');
                const data = await response.json();
                row.classList.toggle('is-complete', Boolean(data.completed));
                button.setAttribute('aria-pressed', String(Boolean(data.completed)));
                button.setAttribute('aria-label', `${data.completed ? 'Unmark' : 'Mark'} ${row.dataset.habitName} as complete`);
                if (status) status.textContent = data.completed ? 'Complete' : 'In progress';
                const weeklyCell = document.querySelector(`[data-habit-cell="${data.habit_id}-${row.dataset.today}"]`);
                if (weeklyCell) weeklyCell.classList.toggle('is-complete', Boolean(data.completed));
            } catch (error) {
                console.error(error);
                if (status) status.textContent = 'Could not save';
            } finally {
                button.disabled = false;
            }
        });
    });

    document.querySelectorAll('[data-open-modal]').forEach((button) => {
        button.addEventListener('click', () => document.getElementById(button.dataset.openModal).classList.add('is-open'));
    });
    document.querySelectorAll('[data-close-modal]').forEach((button) => {
        button.addEventListener('click', () => button.closest('.modal').classList.remove('is-open'));
    });

    document.querySelectorAll('[data-todo-toggle]').forEach((button) => {
        button.addEventListener('click', async () => {
            const response = await fetch(button.dataset.todoToggle, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
            });
            if (response.ok) button.classList.toggle('is-done');
        });
    });

    const focusConsole = document.querySelector('[data-focus-duration]');
    if (focusConsole) {
        const display = focusConsole.querySelector('[data-focus-display]');
        const ring = focusConsole.querySelector('.focus-ring');
        const progress = focusConsole.querySelector('[data-focus-progress]');
        const toggle = focusConsole.querySelector('[data-focus-toggle]');
        const state = focusConsole.querySelector('[data-focus-state]');
        const totalSeconds = Number(focusConsole.dataset.focusDuration) * 60;
        let remaining = totalSeconds;
        let interval = null;
        const render = () => {
            display.textContent = `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;
            const percent = ((totalSeconds - remaining) / totalSeconds) * 100;
            progress.style.width = `${percent}%`;
            ring.style.background = `conic-gradient(var(--blue) ${percent * 3.6}deg, #273241 0deg)`;
        };
        const reset = () => { clearInterval(interval); interval = null; remaining = totalSeconds; toggle.textContent = 'Start focus'; state.textContent = 'Ready when you are.'; render(); };
        const complete = async () => {
            const response = await fetch(focusConsole.dataset.focusCompleteUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
            });
            if (response.ok) {
                const data = await response.json();
                const blocks = document.querySelector('[data-focus-blocks]');
                if (blocks) blocks.textContent = data.blocks;
            }
            reset();
            state.textContent = 'Block complete. Take a breath.';
        };
        toggle.addEventListener('click', () => {
            if (interval) { clearInterval(interval); interval = null; toggle.textContent = 'Resume'; state.textContent = 'Paused.'; return; }
            toggle.textContent = 'Pause'; state.textContent = 'In the zone.';
            interval = setInterval(() => { remaining -= 1; render(); if (remaining <= 0) complete(); }, 1000);
        });
        focusConsole.querySelector('[data-focus-reset]').addEventListener('click', reset);
        focusConsole.querySelector('[data-focus-skip]').addEventListener('click', () => { remaining = Math.min(remaining, 5 * 60); render(); });
        render();
    }

    const display = document.querySelector('[data-timer-display]');
    if (!display) return;
    const toggle = document.querySelector('[data-timer-toggle]');
    const progress = document.querySelector('[data-timer-progress]');
    const totalSeconds = 25 * 60;
    let remaining = totalSeconds;
    let interval = null;

    const render = () => {
        const minutes = String(Math.floor(remaining / 60)).padStart(2, '0');
        const seconds = String(remaining % 60).padStart(2, '0');
        display.textContent = `${minutes}:${seconds}`;
        progress.style.width = `${((totalSeconds - remaining) / totalSeconds) * 100}%`;
    };
    const reset = () => { clearInterval(interval); interval = null; remaining = totalSeconds; toggle.textContent = 'Start focus'; render(); };
    toggle.addEventListener('click', () => {
        if (interval) { clearInterval(interval); interval = null; toggle.textContent = 'Resume focus'; return; }
        toggle.textContent = 'Pause';
        interval = setInterval(() => { remaining -= 1; render(); if (remaining <= 0) reset(); }, 1000);
    });
    document.querySelector('[data-timer-reset]').addEventListener('click', reset);
    document.querySelector('[data-timer-skip]').addEventListener('click', () => { remaining = 5 * 60; render(); });
    render();
})();
