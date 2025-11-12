# app/components/edit_event.py
from __future__ import annotations
from typing import Callable, Dict, Optional, Any
from datetime import datetime
from nicegui import ui

from .reminder_event import ReminderComponent
from .recurring_event import RecurringComponent

_TIME_FORMATS = ['%H:%M','%H:%M:%S','%I:%M %p','%I %p','%I:%M%p','%I%p']

def _parse_time_to_minutes(s: str) -> Optional[int]:
    v = (s or '').strip()
    if not v: return None
    v = ' '.join(v.split())
    for fmt in _TIME_FORMATS:
        try:
            t = datetime.strptime(v, fmt).time()
            return t.hour * 60 + t.minute
        except Exception:
            pass
    return None

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
    title_val = original.get('title', '') or ''
    date_val = original.get('date', '') or ''
    start_val = original.get('start', '') or ''
    end_val = original.get('end', '') or ''
    desc_val = original.get('description', '') or ''

    reminder_comp = ReminderComponent(
        initial_minutes=original.get('reminder_minutes') if isinstance(original.get('reminder_minutes'), list) else None,
        initial_labels=original.get('reminders') if isinstance(original.get('reminders'), list) else None,
    )
    recurring_comp = RecurringComponent(original)

    dialog = ui.dialog()
    with dialog, ui.card().classes('w-[min(92vw,600px)] max-w-full max-h-[85vh] relative'):
        with ui.column().classes('items-center w-full q-gutter-sm'):
            ui.label('Edit Event' if event else 'New Event').classes('text-h6 text-weight-bold q-mb-sm')
            field_w = 'w-[92%] max-w-[460px]'

            # --- Base Event Info ---
            title_inp = ui.input('Title', value=title_val,
                                 validation={'Title is required': _is_nonempty}
                                 ).props('outlined dense clearable').classes(field_w)

            date_inp = ui.input('Date (YYYY-MM-DD)', value=date_val,
                                validation={'Enter a valid date as YYYY-MM-DD': _is_date}
                                ).props('outlined dense clearable').classes(field_w)

            start_inp = ui.input('Start Time', value=start_val,
                                 validation={'Invalid time (e.g., 09:00 or 9:00 AM)': lambda v: True if not (v or '').strip() else (_parse_time_to_minutes(v) is not None)}
                                 ).props('outlined dense clearable').classes(field_w)

            end_inp = ui.input('End Time', value=end_val,
                               validation={'Invalid time (e.g., 10:00 or 1:00 PM)': lambda v: True if not (v or '').strip() else (_parse_time_to_minutes(v) is not None)}
                               ).props('outlined dense clearable').classes(field_w)

            desc_inp = ui.textarea(label='Description', value=desc_val, placeholder='Optional notes, agenda, location, or links…'
                                   ).props('outlined autogrow').classes(field_w)

            ui.separator().classes(f'{field_w} q-my-sm')

            # --- Recurrence & Reminders ---
            recurring_comp.build(width_class=field_w)
            reminder_comp.build(width_class=field_w)

            # --- Footer ---
            with ui.row().classes(f'{field_w} justify-end q-gutter-sm q-mt-md'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                if event and on_delete:
                    ui.button('Delete', on_click=lambda: (on_delete(original), dialog.close())).props('flat color=negative')

                def do_save() -> None:
                    ok = True
                    for comp in (title_inp, date_inp, start_inp, end_inp):
                        ok = comp.validate() and ok

                    _clear_error(end_inp)
                    sm = _parse_time_to_minutes(start_inp.value or '')
                    em = _parse_time_to_minutes(end_inp.value or '')
                    if sm is not None and em is not None and em <= sm:
                        _set_error(end_inp, 'End must be after Start'); ok = False

                    freq_label, interval, until_iso, count_val = recurring_comp.get_values()
                    if freq_label != 'None' and until_iso and _is_date(until_iso) and _is_date(date_inp.value or ''):
                        sd = datetime.strptime(date_inp.value.strip(), '%Y-%m-%d').date()
                        ed = datetime.strptime(until_iso, '%Y-%m-%d').date()
                        if ed < sd:
                            ui.notify('End date must be on/after the event date', color='negative'); ok = False

                    if not ok:
                        ui.notify('Please fix the highlighted fields.', color='negative'); return

                    recurring_text, recurrence = recurring_comp.get_human_and_struct()
                    all_labels, minutes = reminder_comp.get_labels_and_minutes()

                    updated = {
                        'title': (title_inp.value or '').strip(),
                        'date': (date_inp.value or '').strip(),
                        'start': (start_inp.value or '').strip(),
                        'end': (end_inp.value or '').strip(),
                        'recurring': recurring_text,
                        'recurrence': recurrence,
                        'description': (desc_inp.value or ''),
                        'reminders': all_labels,
                        'reminder_minutes': minutes,
                    }
                    on_save(updated)
                    dialog.close()

                ui.button('Save', on_click=do_save).props('color=primary')

    dialog.open()
