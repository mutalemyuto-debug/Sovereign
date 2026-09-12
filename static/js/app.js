(() => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

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
