# app/components/edit_event.py
from __future__ import annotations
from typing import Callable, Dict, Optional, List, Any, Tuple
from datetime import datetime
from nicegui import ui
import re

# -------- Reminders (presets) --------
REMINDER_OPTIONS: Dict[str, int] = {
    'At time of event': 0,
    '5 minutes before': 5,
    '10 minutes before': 10,
    '15 minutes before': 15,
    '30 minutes before': 30,
    '1 hour before': 60,
    '2 hours before': 120,
    '1 day before': 1440,
}
ALL_LABELS: List[str] = list(REMINDER_OPTIONS.keys())

# -------- Time parsing --------
_TIME_FORMATS = [
    '%H:%M',        # 09:05, 23:15
    '%H:%M:%S',     # 09:05:00
    '%I:%M %p',     # 9:05 AM
    '%I %p',        # 9 AM
    '%I:%M%p',      # 9:05AM
    '%I%p',         # 9AM
]

def _parse_time_to_minutes(s: str) -> Optional[int]:
    val = (s or '').strip()
    if not val:
        return None
    val = ' '.join(val.split())  # normalize spacing
    for fmt in _TIME_FORMATS:
        try:
            t = datetime.strptime(val, fmt).time()
            return t.hour * 60 + t.minute
        except Exception:
            continue
    return None

def _is_nonempty(v: str) -> bool:
    return bool(v and v.strip())

def _is_date(v: str) -> bool:
    try:
        datetime.strptime((v or '').strip(), '%Y-%m-%d')
        return True
    except Exception:
        return False

# -------- Reminders helpers --------
def _labels_from_minutes(existing: Optional[List[int]]) -> List[str]:
    if not existing:
        return []
    rev = {v: k for k, v in REMINDER_OPTIONS.items()}
    return [rev.get(m, f'{m} minutes before') for m in sorted(existing)]

def _minutes_from_labels(labels: List[str]) -> List[int]:
    mins: List[int] = []
    for label in labels:
        if label in REMINDER_OPTIONS:
            mins.append(REMINDER_OPTIONS[label])
        else:
            # Accept "X minutes before"
            try:
                mins.append(int(label.split()[0]))
            except Exception:
                pass
    return sorted(set(mins))

# -------- Recurring helpers --------
FREQ_LABELS = ['None', 'Daily', 'Weekly', 'Monthly']
FREQ_TO_RRULE = {'Daily': 'DAILY', 'Weekly': 'WEEKLY', 'Monthly': 'MONTHLY'}

def _parse_recurring_text(text: Optional[str]) -> Tuple[str, int]:
    """
    Parse strings like:
      - "Daily" → ("Daily", 1)
      - "Weekly" → ("Weekly", 1)
      - "Every 3 Months" → ("Monthly", 3)
    Fallback: ("None", 1)
    """
    if not text:
        return 'None', 1
    t = text.strip().lower()
    if t == 'daily':
        return 'Daily', 1
    if t == 'weekly':
        return 'Weekly', 1
    if t == 'monthly':
        return 'Monthly', 1

    m = re.match(r'^\s*every\s+(\d+)\s+(day|days)\s*$', t)
    if m:
        return 'Daily', max(1, int(m.group(1)))

    m = re.match(r'^\s*every\s+(\d+)\s+(week|weeks)\s*$', t)
    if m:
        return 'Weekly', max(1, int(m.group(1)))

    m = re.match(r'^\s*every\s+(\d+)\s+(month|months)\s*$', t)
    if m:
        return 'Monthly', max(1, int(m.group(1)))

    return 'None', 1

def _recurring_human(freq_label: str, interval: int) -> Optional[str]:
    if freq_label == 'None':
        return None
    if interval <= 1:
        return freq_label
    unit = {'Daily': 'Days', 'Weekly': 'Weeks', 'Monthly': 'Months'}[freq_label]
    return f'Every {interval} {unit}'

# Small helpers to force red highlight on cross-field errors
def _set_error(inp: ui.input, msg: str) -> None:
    inp.props(f'error=true error-message="{msg}"')

def _clear_error(inp: ui.input) -> None:
    inp.props('error=false error-message=""')

# -------- Main dialog --------
def open_edit_dialog(
    event: Optional[Dict[str, Any]],
    on_save: Callable[[Dict[str, Any]], None],
    on_delete: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> None:
    """
    Dialog for editing/creating events.
    - Validates ONLY on Save (invalid fields highlight red).
    - End time must be after start time (when both provided).
    - Recurring is chosen via (None/Daily/Weekly/Monthly) + interval number.
    """
    original = event or {}
    title_val = original.get('title', '') or ''
    date_val = original.get('date', '') or ''
    start_val = original.get('start', '') or ''
    end_val = original.get('end', '') or ''
    desc_val = original.get('description', '') or ''

    # Prefill recurring controls from the old 'recurring' string
    rec_label0, rec_interval0 = _parse_recurring_text(original.get('recurring'))

    # Seed reminders from existing fields
    if isinstance(original.get('reminder_minutes'), list):
        initial_labels = _labels_from_minutes(original['reminder_minutes'])
    elif isinstance(original.get('reminders'), list):
        initial_labels = [l for l in original['reminders'] if isinstance(l, str)]
    else:
        initial_labels = []

    selected_preset_labels: List[str] = [l for l in ALL_LABELS if l in initial_labels]
    custom_minutes: List[int] = sorted({
        int(l.split()[0]) for l in initial_labels
        if isinstance(l, str) and l.endswith('minutes before') and l.split()[0].isdigit()
    })

    dialog = ui.dialog()
    with dialog, ui.card().classes('w-[min(92vw,600px)] max-w-full max-h-[85vh] relative'):
        with ui.column().classes('items-center w-full q-gutter-sm'):
            ui.label('Edit Event' if event else 'New Event').classes('text-h6 text-weight-bold q-mb-sm')

            field_w = 'w-[92%] max-w-[460px]'

            # --- Inputs (save-time validation) ---
            title_inp = ui.input(
                'Title', value=title_val,
                validation={'Title is required': _is_nonempty},
            ).props('outlined dense clearable').classes(field_w)

            date_inp = ui.input(
                'Date (YYYY-MM-DD)', value=date_val,
                validation={'Enter a valid date as YYYY-MM-DD': _is_date},
            ).props('outlined dense clearable').classes(field_w)

            start_inp = ui.input(
                'Start Time', value=start_val,
                validation={'Invalid time (e.g., 09:00 or 9:00 AM)': lambda v: True if not (v or '').strip() else (_parse_time_to_minutes(v) is not None)},
            ).props('outlined dense clearable').classes(field_w)

            # End time cross-field rule handled on save
            end_inp = ui.input(
                'End Time', value=end_val,
                validation={'Invalid time (e.g., 10:00 or 1:00 PM)': lambda v: True if not (v or '').strip() else (_parse_time_to_minutes(v) is not None)},
            ).props('outlined dense clearable').classes(field_w)

            desc_inp = ui.textarea(
                label='Description',
                value=desc_val,
                placeholder='Optional notes, agenda, location, or links…',
            ).props('outlined autogrow').classes(field_w)

            ui.separator().classes(f'{field_w} q-my-sm')

            # --- Recurring controls ---
            ui.label('Recurring').classes('text-body2 text-weight-medium self-start q-ml-md')
            with ui.row().classes(f'{field_w} items-center gap-3'):
                recurring_sel = ui.select(
                    options=FREQ_LABELS,
                    value=rec_label0,
                    label='Frequency',
                ).props('outlined dense').classes('min-w-[160px]')
                interval_inp = ui.number(
                    label='Every … (interval)',
                    value=rec_interval0,
                    min=1, max=365,
                ).props('outlined dense').classes('w-[160px]')

            # Disable interval when 'None'
            def _toggle_interval():
                interval_inp.props(f'disable={"true" if recurring_sel.value == "None" else "false"}')
            _toggle_interval()
            recurring_sel.on('update:model-value', lambda _: _toggle_interval())

            # --- Reminders (presets + custom minutes) ---
            ui.separator().classes(f'{field_w} q-my-sm')
            ui.label('Reminders').classes('text-body2 text-weight-medium self-start q-ml-md')

            with ui.element('div').classes(f'{field_w} grid grid-cols-1 md:grid-cols-2 gap-2'):
                preset_checkboxes: Dict[str, ui.element] = {}
                for label in ALL_LABELS:
                    cb = ui.checkbox(label, value=(label in selected_preset_labels))
                    preset_checkboxes[label] = cb

            with ui.row().classes(f'{field_w} items-center justify-start q-gutter-sm q-mt-sm'):
                ui.label('Custom (minutes before):').classes('text-caption text-grey-7')
                custom_input = ui.number(value=None, min=1, max=10080).props('outlined dense').classes('w-[120px]')

                def refresh_custom_chips():
                    custom_wrap.clear()
                    with custom_wrap:
                        for m in sorted(set(custom_minutes)):
                            ui.chip(f'{m} min').props('outline')

                def add_custom():
                    val = custom_input.value
                    try:
                        m = int(val)
                    except Exception:
                        ui.notify('Custom minutes must be a number', color='negative')
                        return
                    if m <= 0 or m > 10080:
                        ui.notify('Custom minutes must be between 1 and 10080 (7 days)', color='negative')
                        return
                    if m not in custom_minutes:
                        custom_minutes.append(m)
                        refresh_custom_chips()
                        custom_input.value = None

                ui.button('Add', on_click=add_custom).props('dense')
                custom_wrap = ui.row().classes('q-gutter-xs items-center')
                refresh_custom_chips()
                custom_input.on('keydown.enter', add_custom)

            with ui.row().classes(f'{field_w} justify-between q-mt-xs'):
                ui.button(
                    'Select all presets',
                    on_click=lambda: [setattr(preset_checkboxes[l], 'value', True) for l in ALL_LABELS],
                ).props('flat dense')

                def clear_all():
                    [setattr(preset_checkboxes[l], 'value', False) for l in ALL_LABELS]
                    custom_minutes.clear()
                    refresh_custom_chips()
                ui.button('Clear all', on_click=clear_all).props('flat dense')

            # --- Footer ---
            with ui.row().classes(f'{field_w} justify-end q-gutter-sm q-mt-md'):
                ui.button('Cancel', on_click=dialog.close).props('flat')

                if event and on_delete:
                    def _do_delete() -> None:
                        on_delete(original)
                        dialog.close()
                    ui.button('Delete', on_click=_do_delete).props('flat color=negative')

                def do_save() -> None:
                    ok = True

                    # Built-in field validations first
                    for comp in (title_inp, date_inp, start_inp, end_inp):
                        ok = comp.validate() and ok

                    # Cross-field: end after start (when both present & valid)
                    _clear_error(end_inp)
                    sm = _parse_time_to_minutes(start_inp.value or '')
                    em = _parse_time_to_minutes(end_inp.value or '')
                    if sm is not None and em is not None and em <= sm:
                        _set_error(end_inp, 'End must be after Start')
                        ok = False

                    # Recurring interval required if frequency != None
                    _clear_error(interval_inp)
                    freq = recurring_sel.value or 'None'
                    try:
                        interval = int(interval_inp.value) if interval_inp.value is not None else 0
                    except Exception:
                        interval = 0
                    if freq != 'None' and interval < 1:
                        _set_error(interval_inp, 'Enter a positive interval (e.g., 1, 2, 3)')
                        ok = False

                    if not ok:
                        ui.notify('Please fix the highlighted fields.', color='negative')
                        return

                    # Build recurrence fields
                    if freq == 'None':
                        recurring_text = None
                        recurrence = None
                    else:
                        recurring_text = _recurring_human(freq, interval)
                        recurrence = {'freq': FREQ_TO_RRULE[freq], 'interval': interval}

                    # Gather reminders
                    selected_presets = [l for l, cb in preset_checkboxes.items() if cb.value]
                    labels_from_custom = [f'{m} minutes before' for m in sorted(set(custom_minutes))]
                    all_labels = selected_presets + labels_from_custom
                    reminder_minutes = _minutes_from_labels(all_labels)

                    updated = {
                        'title': (title_inp.value or '').strip(),
                        'date': (date_inp.value or '').strip(),
                        'start': (start_inp.value or '').strip(),
                        'end': (end_inp.value or '').strip(),
                        'recurring': recurring_text,  # human-readable for your current cards
                        'recurrence': recurrence,     # structured for future logic
                        'description': (desc_inp.value or ''),
                        'reminders': all_labels,
                        'reminder_minutes': reminder_minutes,
                    }
                    on_save(updated)
                    dialog.close()

                ui.button('Save', on_click=do_save).props('color=primary')

    dialog.open()
