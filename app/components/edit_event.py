# app/components/edit_event.py
from __future__ import annotations
from typing import Callable, Dict, Optional, List
from nicegui import ui

# Map human-friendly reminder labels to minute offsets
REMINDER_OPTIONS = {
    'None': None,
    'At time of event': 0,
    '5 minutes before': 5,
    '10 minutes before': 10,
    '15 minutes before': 15,
    '30 minutes before': 30,
    '1 hour before': 60,
    '2 hours before': 120,
    '1 day before': 1440,
}

def _labels_from_minutes(existing: Optional[List[int]]) -> List[str]:
    """Convert stored minute offsets to labels when reopening the dialog."""
    if not existing:
        return []
    rev = {v: k for k, v in REMINDER_OPTIONS.items() if v is not None}
    labels = []
    for m in existing:
        if m in rev:
            labels.append(rev[m])
        else:
            labels.append(f'{m} minutes before')  # fallback for custom values
    return labels

def _minutes_from_labels(labels: List[str]) -> List[int]:
    """Convert selected labels into minute offsets (filtering out 'None')."""
    mins: List[int] = []
    for label in labels:
        if label == 'None':
            continue
        if label in REMINDER_OPTIONS and REMINDER_OPTIONS[label] is not None:
            mins.append(REMINDER_OPTIONS[label])  # type: ignore[arg-type]
        else:
            # Try to parse "X minutes before"
            try:
                num = int(label.split()[0])
                mins.append(num)
            except Exception:
                pass
    return mins

def open_edit_dialog(
    event: Optional[Dict[str, str]],
    on_save: Callable[[Dict[str, str]], None],
    on_delete: Optional[Callable[[Dict[str, str]], None]] = None,
) -> None:
    """
    Open a modal dialog to create or edit an event.

    Adds:
      - description (multiline)
      - reminders (multi-select; returns both labels and minute offsets)
    """
    original = event or {}
    title_val = original.get('title', '')
    date_val = original.get('date', '')
    start_val = original.get('start', '')
    end_val = original.get('end', '')
    recurring_val = original.get('recurring', '') or ''
    desc_val = original.get('description', '') or ''

    # Accept either 'reminder_minutes' (list[int]) or 'reminders' (list[str])
    existing_min = original.get('reminder_minutes')
    existing_labels = original.get('reminders')
    if isinstance(existing_min, list):
        reminders_initial = _labels_from_minutes(existing_min)
    elif isinstance(existing_labels, list):
        reminders_initial = [l for l in existing_labels if l in REMINDER_OPTIONS or l.endswith('minutes before')]
    else:
        reminders_initial = []

    dialog = ui.dialog()
    with dialog, ui.card().classes('w-[min(92vw,560px)] max-w-full'):
        ui.label('Edit Event' if event else 'New Event').classes('text-h6 text-weight-bold q-mb-sm')

        # --- Basic fields ---
        title_inp = ui.input(
            label='Title',
            value=title_val,
            placeholder='e.g., Team Sync',
        ).props('outlined dense clearable').classes('q-mb-sm')

        date_inp = ui.input(
            label='Date (YYYY-MM-DD)',
            value=date_val,
            placeholder='e.g., 2025-01-08',
        ).props('outlined dense clearable').classes('q-mb-sm')

        start_inp = ui.input(
            label='Start Time',
            value=start_val,
            placeholder='e.g., 09:00 AM',
        ).props('outlined dense clearable').classes('q-mb-sm')

        end_inp = ui.input(
            label='End Time',
            value=end_val,
            placeholder='e.g., 10:00 AM',
        ).props('outlined dense clearable').classes('q-mb-sm')

        recurring_inp = ui.input(
            label='Recurring',
            value=recurring_val,
            placeholder='e.g., Daily / Weekly / Every 2 Weeks',
        ).props('outlined dense clearable').classes('q-mb-md')

        # --- Description (multiline) ---
        desc_inp = ui.textarea(
            label='Description',
            value=desc_val,
            placeholder='Optional notes, agenda, location, links…',
        ).props('outlined autogrow').classes('q-mb-md')

        # --- Reminders (multiple select with chips) ---
        reminder_labels = list(REMINDER_OPTIONS.keys())
        # Remove 'None' from the dropdown itself; clearing selections = no reminders
        if 'None' in reminder_labels:
            reminder_labels.remove('None')

        reminder_sel = ui.select(
            options=reminder_labels,
            value=reminders_initial,
            label='Reminders',  # <-- use label instead of placeholder
        ).props('outlined dense multiple use-chips clearable').classes('q-mb-md')

        with ui.row().classes('justify-end q-gutter-sm'):
            ui.button('Cancel', on_click=dialog.close).props('flat')

            if event and on_delete:
                def _do_delete():
                    on_delete(original)
                    dialog.close()
                ui.button('Delete', on_click=_do_delete).props('flat color=negative')

            def _do_save():
                # Normalize reminders
                selected_labels = (reminder_sel.value or []) if isinstance(reminder_sel.value, list) else []
                reminder_minutes = _minutes_from_labels(selected_labels)

                updated = {
                    'title': title_inp.value or '',
                    'date': date_inp.value or '',
                    'start': start_inp.value or '',
                    'end': end_inp.value or '',
                    'recurring': (recurring_inp.value or '') or None,
                    'description': desc_inp.value or '',
                    # store both for convenience:
                    'reminders': selected_labels,          # human readable
                    'reminder_minutes': reminder_minutes,   # numeric offsets
                }
                on_save(updated)
                dialog.close()

            ui.button('Save', on_click=_do_save).props('color=primary')

    dialog.open()
