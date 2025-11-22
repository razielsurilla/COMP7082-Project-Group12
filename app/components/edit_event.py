# app/components/edit_event.py
from __future__ import annotations
from typing import Callable, Dict, Optional, Any
from datetime import datetime
from nicegui import ui

from .reminder_event import ReminderComponent
from .recurring_event import RecurringComponent
from .addedit import datePickerLabel, timePickerLabel


_TIME_FORMATS = ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I %p', '%I:%M%p', '%I%p']

# Map RecurringComponent's labels to a small index
_FREQ_TO_INDEX = {
    'None': 0,
    'Daily': 1,
    'Weekly': 2,
    'Monthly': 3,
}


def _parse_time_to_minutes(s: str) -> Optional[int]:
    v = (s or '').strip()
    if not v:
        return None
    v = ' '.join(v.split())
    for fmt in _TIME_FORMATS:
        try:
            t = datetime.strptime(v, fmt).time()
            return t.hour * 60 + t.minute
        except Exception:
            pass
    return None


def _minutes_to_12h_str(minutes: Optional[int]) -> str:
    """Convert minutes from midnight to 'H:MM AM/PM' (no leading zero on hour)."""
    if minutes is None:
        return ''
    h = minutes // 60
    m = minutes % 60
    dt = datetime(2000, 1, 1, h, m)
    s = dt.strftime('%I:%M %p')  # e.g. '09:00 AM'
    if s.startswith('0'):
        s = s[1:]
    return s


def _to_time_input_value(s: str) -> str:
    """
    Convert any supported time string (e.g. '9:00 AM') to HTML <input type="time">
    value 'HH:MM'. Returns '' if it can't be parsed.
    """
    mins = _parse_time_to_minutes(s)
    if mins is None:
        return ''
    h = mins // 60
    m = mins % 60
    return f'{h:02d}:{m:02d}'


def _valid_time_required(v: str) -> bool:
    """Time must be non-empty and parseable."""
    v = (v or '').strip()
    return bool(v and _parse_time_to_minutes(v) is not None)


def _is_nonempty(v: str) -> bool:
    return bool(v and v.strip())


def _is_date(v: str) -> bool:
    try:
        datetime.strptime((v or '').strip(), '%Y-%m-%d')
        return True
    except Exception:
        return False


def _set_error(inp: ui.input, msg: str) -> None:
    inp.props(f'error=true error-message="{msg}"')


def _clear_error(inp: ui.input) -> None:
    inp.props('error=false error-message=""')


def open_edit_dialog(
    event: Optional[Dict[str, Any]],
    on_save: Callable[[Dict[str, Any]], None],
    on_delete: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> None:
    """Compose Event + Recurrence + Reminders into a single dialog."""
    original = event or {}

    # Prefer 'start_date', fall back to legacy 'date'
    title_val = original.get('title', '') or ''
    start_date_val = original.get('start_date') or original.get('date') or ''
    end_date_val = original.get('end_date', '') or ''
    start_val = original.get('start', '') or ''
    end_val = original.get('end', '') or ''
    desc_val = original.get('description', '') or ''

    reminder_comp = ReminderComponent(
        initial_minutes=original.get('reminder_minutes')
        if isinstance(original.get('reminder_minutes'), list) else None,
        initial_labels=original.get('reminders')
        if isinstance(original.get('reminders'), list) else None,
    )
    recurring_comp = RecurringComponent(original)

    dialog = ui.dialog()
    with dialog, ui.card().classes('w-[min(92vw,600px)] max-w-full max-h-[85vh] relative'):
        with ui.column().classes('items-center w-full q-gutter-sm'):
            ui.label('Edit Event' if event else 'New Event').classes(
                'text-h6 text-weight-bold q-mb-sm'
            )
            field_w = 'w-[92%] max-w-[460px]'

            # --- Base Event Info ---
            title_inp = ui.input(
                'Title',
                value=title_val,
                validation={
                    'Title is required (e.g., "Lab meeting")': _is_nonempty
                },
            ).props('outlined dense clearable').classes(f'{field_w} pb-0')

            with ui.grid().classes(
                "grid-cols-1 md:grid-cols-2 gap-2 w-full max-w-[460px]"
            ):
                # Row 1
                start_date_inp = datePickerLabel('Start Date', None, start_date_val)
                end_date_inp = datePickerLabel('End Date', None, end_date_val)

                # Row 2
                start_inp = timePickerLabel('Start Time', None, start_val)
                end_inp = timePickerLabel('End Time', None, end_val)

            desc_inp = ui.textarea(
                label='Description',
                value=desc_val,
                placeholder='Optional notes, agenda, location, or links…',
            ).props('outlined autogrow').classes(field_w)

            ui.separator().classes(f'{field_w} q-my-sm')

            # --- Recurrence & Reminders ---
            recurring_comp.build(width_class=field_w)
            reminder_comp.build(width_class=field_w)

            # --- Footer ---
            with ui.row().classes(f'{field_w} justify-end q-gutter-sm q-mt-md'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                if event and on_delete:
                    ui.button(
                        'Delete',
                        on_click=lambda: (on_delete(original), dialog.close()),
                    ).props('flat color=negative')

                def do_save() -> None:
                    ok = True

                    # Field-level validation first
                    for comp in (title_inp, start_date_inp, end_date_inp, start_inp, end_inp):
                        ok = comp.validate() and ok

                    # Cross-field validation for time ordering
                    _clear_error(end_inp)
                    raw_start = start_inp.value or ''
                    raw_end = end_inp.value or ''

                    sm = _parse_time_to_minutes(raw_start)
                    em = _parse_time_to_minutes(raw_end)

                    if sm is None or em is None:
                        # Should already be caught by validation, but just in case:
                        _set_error(end_inp, 'Please select both a start and an end time.')
                        ok = False
                    elif em <= sm:
                        _set_error(end_inp, 'End time must be later than start time.')
                        ok = False

                    # End date not before start date
                    sd_str = (start_date_inp.value or '').strip()
                    ed_str = (end_date_inp.value or '').strip()
                    if sd_str and ed_str and _is_date(sd_str) and _is_date(ed_str):
                        sd = datetime.strptime(sd_str, '%Y-%m-%d').date()
                        ed = datetime.strptime(ed_str, '%Y-%m-%d').date()
                        if ed < sd:
                            ui.notify(
                                'End date must be on or after the start date.',
                                color='negative',
                            )
                            ok = False

                    # Recurrence validation & values from RecurringComponent
                    freq_label, interval, until_iso, count_val = recurring_comp.get_values()
                    if (
                        freq_label != 'None'
                        and until_iso
                        and _is_date(until_iso)
                        and _is_date(start_date_inp.value or '')
                    ):
                        sd = datetime.strptime(
                            start_date_inp.value.strip(), '%Y-%m-%d'
                        ).date()
                        rd = datetime.strptime(until_iso, '%Y-%m-%d').date()
                        if rd < sd:
                            ui.notify(
                                'Recurrence "Until" date must be on or after the event date.',
                                color='negative',
                            )
                            ok = False

                    if not ok:
                        ui.notify(
                            'Please fix the highlighted fields before saving.',
                            color='negative',
                        )
                        return

                    # Recurrence & reminders payloads
                    recurring_text, recurrence = recurring_comp.get_human_and_struct()
                    all_labels, minutes = reminder_comp.get_labels_and_minutes()

                    # Convert picker values back to friendly 12h display strings
                    sm = _parse_time_to_minutes(raw_start)
                    em = _parse_time_to_minutes(raw_end)
                    start_display = _minutes_to_12h_str(sm)
                    end_display = _minutes_to_12h_str(em)

                    # --- Extra fields for SQL / data layer ---
                    is_recurring_flag = freq_label != 'None'
                    recurring_index = _FREQ_TO_INDEX.get(freq_label, 0)
                    is_alerting_flag = bool(minutes)

                    # interval from RecurringComponent → recurring_interval
                    recurring_interval = interval or 0

                    # Map end options to index + values:
                    # 0 = never, 1 = until date, 2 = after X occurrences
                    recurring_end_option_index = 0
                    recurring_end_date_str: Optional[str] = None
                    recurring_end_count: Optional[int] = None

                    if is_recurring_flag:
                        if until_iso and _is_date(until_iso):
                            recurring_end_option_index = 1
                            recurring_end_date_str = until_iso.strip()
                        elif isinstance(count_val, int) and count_val > 0:
                            recurring_end_option_index = 2
                            recurring_end_count = int(count_val)
                        else:
                            recurring_end_option_index = 0

                    updated = {
                        'title': (title_inp.value or '').strip(),

                        # store dates back in both legacy + new forms
                        'start_date': (start_date_inp.value or '').strip(),
                        'date': (start_date_inp.value or '').strip(),       # legacy key
                        'end_date': (end_date_inp.value or '').strip(),

                        'start': start_display,                             # e.g. '9:00 AM'
                        'end': end_display,                                 # e.g. '10:30 AM'
                        'recurring': recurring_text,
                        'recurrence': recurrence,
                        'description': (desc_inp.value or ''),
                        'reminders': all_labels,
                        'reminder_minutes': minutes,

                        # DB / DTO-friendly fields:
                        'is_recurring': is_recurring_flag,
                        'recurring_option_index': recurring_index,
                        'recurring_interval': recurring_interval,
                        'is_alerting': is_alerting_flag,
                        'selectedAlertCheckboxes': all_labels,

                        # End-option structure
                        'recurring_end_option_index': recurring_end_option_index,
                        'recurring_end_date': recurring_end_date_str,   # ISO date string or None
                        'recurring_end_count': recurring_end_count,     # int or None
                    }

                    on_save(updated)
                    dialog.close()

                ui.button('Save', on_click=do_save).props('color=primary')

    dialog.open()
