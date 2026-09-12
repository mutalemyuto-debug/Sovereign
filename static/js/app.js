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
            try {
                const response = await fetch(button.dataset.habitToggle, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
                });
                if (!response.ok) throw new Error('Habit update failed');
                const data = await response.json();
                const row = document.querySelector(`[data-habit-id="${data.habit_id}"]`);
                row.classList.toggle('is-complete', data.completed);
                row.querySelector('.habit-status').textContent = data.completed ? 'Complete' : 'In progress';
            } catch (error) {
                console.error(error);
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
