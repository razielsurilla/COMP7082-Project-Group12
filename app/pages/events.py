# app/pages/events.py
from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from nicegui import ui
from app.components.edit_event import open_edit_dialog
from app.sharedVars import AddEditEventData  # used to create DB records


# ----------------------------------------------------
# DEMO DATA: used when no calendar_data is provided
#   and also used to SEED the DB when it's empty
# ----------------------------------------------------
def _demo_events() -> List[Dict[str, Any]]:
    return [
        {
            'id': 1,
            'title': 'Morning Standup',
            'date': '2025-01-08',
            'start': '9:00 AM',
            'end': '9:30 AM',
            'recurring': 'Daily',
        },
        {
            'id': 2,
            'title': 'Design Review',
            'date': '2025-01-09',
            'start': '1:00 PM',
            'end': '2:00 PM',
            'recurring': None,
        },
        {
            'id': 3,
            'title': 'Lab Meeting',
            'date': '2025-01-10',
            'start': '10:00 AM',
            'end': '11:30 AM',
            'recurring': 'Weekly',
        },
        {
            'id': 4,
            'title': 'Team Lunch',
            'date': '2025-02-01',
            'start': '12:00 PM',
            'end': '1:00 PM',
            'recurring': None,
        },
    ]


def _date_badge(iso_date: str) -> str:
    d = datetime.fromisoformat(iso_date).date()
    return f"{d.strftime('%b').upper()} {d.day}"


def _format_time_12h(dt: datetime) -> str:
    """Return times like '9:00 AM' / '1:05 PM' (no leading zero on hour)."""
    s = dt.strftime('%I:%M %p')  # e.g. '09:00 AM'
    if s.startswith('0'):
        s = s[1:]
    return s


def _parse_date_time(date_str: str, time_str: str) -> float:
    """
    Combine 'YYYY-MM-DD' with '9:00 AM' or '09:00' into a Unix timestamp.
    """
    date_str = (date_str or '').strip()
    time_str = (time_str or '').strip()

    if not date_str or not time_str:
        raise ValueError("Missing date or time for event")

    joined = f'{date_str} {time_str}'

    # Try 12h then 24h
    for fmt in ('%Y-%m-%d %I:%M %p', '%Y-%m-%d %H:%M'):
        try:
            dt = datetime.strptime(joined, fmt)
            return dt.timestamp()
        except ValueError:
            continue

    raise ValueError(f"Cannot parse date/time: '{joined}'")


def _freq_index_from_text(recurring_text: Optional[str], fallback_idx: int = 0) -> int:
    """
    Map human recurring text ('Daily', 'Every 2 Weeks', etc.) to
    an index: 0=None, 1=Daily, 2=Weekly, 3=Monthly.
    """
    if not recurring_text:
        return fallback_idx
    t = recurring_text.lower()
    if 'daily' in t or 'day' in t:
        return 1
    if 'weekly' in t or 'week' in t:
        return 2
    if 'monthly' in t or 'month' in t:
        return 3
    return fallback_idx


# --------------------------------------------
# Main page
# --------------------------------------------
def show(calendar_data: Optional[Any] = None) -> None:
    """Events page with simple search and integrated Edit/Delete/New via dialog component."""

    # --------------------------------------------
    # Helper: convert AddEditEventData -> UI dict
    # --------------------------------------------
    def _from_data_frame(df: Any) -> Dict[str, Any]:
        """
        df is an AddEditEventData from CalendarData.getAllData()
        """
        start_dt = datetime.fromtimestamp(df.eventStartDate)
        end_dt = datetime.fromtimestamp(df.eventEndDate)

        date_str = start_dt.strftime('%Y-%m-%d')
        start_str = _format_time_12h(start_dt)
        end_str = _format_time_12h(end_dt)

        # Map recurringEventOptionIndex -> label
        idx = int(getattr(df, 'recurringEventOptionIndex', 0) or 0)
        freq_labels = ['None', 'Daily', 'Weekly', 'Monthly']
        freq_label = freq_labels[idx] if 0 <= idx < len(freq_labels) else 'None'
        recurring_label = None if freq_label == 'None' else freq_label

        # Decode JSON from DB if needed
        raw_alert = getattr(df, 'selectedAlertCheckboxes', []) or []
        if isinstance(raw_alert, str):
            try:
                alert_labels = json.loads(raw_alert)
            except Exception:
                alert_labels = []
        else:
            # Ensure it is a list of strings
            alert_labels = [str(x) for x in raw_alert]

        ev: Dict[str, Any] = {
            # Use the timestamps as a stable composite identity
            'id': f'{df.eventStartDate}-{df.eventEndDate}',
            'title': df.eventName,
            'date': date_str,
            'start': start_str,
            'end': end_str,
            'recurring': recurring_label,
            # Hidden fields for DB operations:
            '_start_ts': df.eventStartDate,
            '_end_ts': df.eventEndDate,
            # Optional extras
            'description': getattr(df, 'eventDescription', '') or '',
            'is_recurring': bool(getattr(df, 'isRecurringEvent', False)),
            'is_alerting': bool(getattr(df, 'isAlerting', False)),
            'recurring_option_index': idx,
            'selectedAlertCheckboxes': alert_labels,
            # For ReminderComponent (used as initial_labels)
            'reminders': alert_labels,
            # We don't store reminder_minutes in DB yet; ReminderComponent
            # will infer minutes from the labels.
        }
        return ev

    # --------------------------------------------
    # Seed demo events into DB if empty
    # --------------------------------------------
    def _seed_demo_events_if_empty() -> None:
        if calendar_data is None:
            return

        frames = calendar_data.getAllData()
        if frames:
            return

        for d in _demo_events():
            frame = AddEditEventData()
            frame.eventName = d['title']
            frame.eventStartDate = _parse_date_time(d['date'], d['start'])
            frame.eventEndDate = _parse_date_time(d['date'], d['end'])
            frame.eventDescription = ''
            # recurrence
            rec_text = d.get('recurring')
            idx = _freq_index_from_text(rec_text, 0)
            frame.isRecurringEvent = bool(idx)
            frame.recurringEventOptionIndex = idx
            # reminders / alerting
            frame.isAlerting = False
            frame.selectedAlertCheckboxes = []

            calendar_data.addData(frame)

    # DB HOOK 1: INITIAL LOAD
    if calendar_data is None:
        events: List[Dict[str, Any]] = _demo_events()
    else:
        _seed_demo_events_if_empty()
        frames = calendar_data.getAllData()
        events = [_from_data_frame(f) for f in frames]

    ui.add_head_html('<style>html, body, #app { overflow-x: hidden !important; }</style>')

    # Header
    with ui.row().classes('items-center justify-between w-full max-w-[100vw] px-4 md:px-6 pt-4'):
        ui.label().classes('w-[14rem] md:w-[20rem]')
        ui.label('Events').classes('text-h5 text-weight-bold text-black text-center flex-1')
        search_box = ui.input(placeholder='Search title or date…') \
            .props('outlined dense clearable debounce=200') \
            .classes('w-[14rem] md:w-[20rem] max-w-full bg-gray-200')

    container = ui.element('div').classes('w-full max-w-[100vw] px-4 md:px-6 pb-24')

    # --------------------------------------------
    # Helpers
    # --------------------------------------------
    def _find_index(original: Dict[str, Any]) -> int:
        oid = original.get('id')
        if oid is not None:
            for i, e in enumerate(events):
                if e.get('id') == oid:
                    return i
        for i, e in enumerate(events):
            if e is original or e == original:
                return i
        return -1

    def refresh_from_db():
        """DB HOOK 2: RELOAD LIST from DB after create/update/delete."""
        nonlocal events
        if calendar_data is not None:
            frames2 = calendar_data.getAllData()
            events = [_from_data_frame(f) for f in frames2]

    def refresh():
        container.clear()
        q = (search_box.value or '').strip().lower()
        filtered: List[Dict[str, Any]] = []
        if q:
            for e in events:
                hay = ' '.join([
                    str(e.get('title', '')),
                    str(e.get('date', '')),
                    str(e.get('start', '')),
                    str(e.get('end', '')),
                    str(e.get('recurring', '')),
                ]).lower()
                if q in hay:
                    filtered.append(e)
        else:
            filtered = events

        with container:
            with ui.element('div').classes('grid grid-cols-1 md:grid-cols-2 gap-6 justify-items-center w-full pl-10'):
                for evt in filtered:
                    _event_card(evt)

    # --------------------------------------------
    # CRUD handlers
    # --------------------------------------------
    def _update_event(original: Dict[str, Any], updated: Dict[str, Any]) -> None:
        """Edit -> Save"""
        if calendar_data is not None:
            old_start_ts = original.get('_start_ts')
            old_end_ts = original.get('_end_ts')

            if old_start_ts is not None and old_end_ts is not None:
                try:
                    # Build new timestamps
                    date_str = updated.get('date', '')
                    start_str = updated.get('start', '')
                    end_str = updated.get('end', '')

                    new_start_ts = _parse_date_time(date_str, start_str)
                    new_end_ts = _parse_date_time(date_str, end_str)

                    # Build new AddEditEventData frame
                    frame = AddEditEventData()
                    frame.eventName = updated.get('title', '') or ''
                    frame.eventStartDate = new_start_ts
                    frame.eventEndDate = new_end_ts
                    frame.eventDescription = updated.get('description', '') or ''
                    frame.isRecurringEvent = bool(updated.get('is_recurring') or updated.get('recurring'))
                    frame.isAlerting = bool(updated.get('is_alerting', False))
                    frame.recurringEventOptionIndex = int(updated.get('recurring_option_index', 0) or 0)
                    frame.selectedAlertCheckboxes = updated.get('selectedAlertCheckboxes', []) or []

                    # ✅ Use your existing updateEvent helper
                    calendar_data.updateEvent(
                        old_start_ts,     # original keys
                        old_end_ts,
                        frame             # new data
                    )

                    # Update UI hidden keys
                    updated['_start_ts'] = new_start_ts
                    updated['_end_ts'] = new_end_ts
                    updated['id'] = f'{new_start_ts}-{new_end_ts}'

                except Exception as e:
                    print(f"[EVENTS] updateEvent error: {e}")
                    ui.notify('Failed to update event in the database (events).', color='negative')
                    return

        # Local update
        i = _find_index(original)
        if i >= 0:
            events[i] = updated
        else:
            events.append(updated)

        if calendar_data is not None:
            refresh_from_db()
        refresh()


    def _remove_event(original: Dict[str, Any]) -> None:
        """Delete"""

        if calendar_data is not None:
            old_start_ts = original.get('_start_ts')
            old_end_ts = original.get('_end_ts')

            if old_start_ts is not None and old_end_ts is not None:
                try:
                    # ✅ use your CalendarData SQL helper instead of raw SQL
                    calendar_data.deleteEvent(old_start_ts, old_end_ts)
                except Exception as e:
                    print(f"[EVENTS] deleteEvent error: {e}")
                    ui.notify('Error deleting event from database (events).', color='negative')
                    return

        # Local list sync
        i = _find_index(original)
        if i >= 0:
            events.pop(i)

        if calendar_data is not None:
            refresh_from_db()
        refresh()

    def _create_event(new_ev: Dict[str, Any]) -> None:
        """New -> Save"""

        if calendar_data is not None:
            date_str = new_ev.get('date', '')
            start_str = new_ev.get('start', '')
            end_str = new_ev.get('end', '')

            start_ts = _parse_date_time(date_str, start_str)
            end_ts = _parse_date_time(date_str, end_str)

            frame = AddEditEventData()
            frame.eventName = new_ev.get('title', '') or ''
            frame.eventStartDate = start_ts
            frame.eventEndDate = end_ts
            frame.eventDescription = new_ev.get('description', '') or ''
            frame.isRecurringEvent = bool(new_ev.get('is_recurring') or new_ev.get('recurring'))
            frame.isAlerting = bool(new_ev.get('is_alerting', False))
            frame.recurringEventOptionIndex = int(new_ev.get('recurring_option_index', 0) or 0)
            frame.selectedAlertCheckboxes = new_ev.get('selectedAlertCheckboxes', []) or []

            try:
                calendar_data.addData(frame)
            except Exception as e:
                print(f"[EVENTS] DB create error: {e}")
                ui.notify('Error saving new event to database.', color='negative')
                return

            # Attach hidden fields so later edits/deletes know their DB keys
            new_ev['_start_ts'] = start_ts
            new_ev['_end_ts'] = end_ts
            new_ev['id'] = f'{start_ts}-{end_ts}'

        events.append(new_ev)

        if calendar_data is not None:
            refresh_from_db()
        refresh()

    # --------------------------------------------
    # One event card
    # --------------------------------------------
    def _event_card(evt: Dict[str, Any]) -> None:
        with ui.card().classes(
            'w-full max-w-[95%] md:max-w-[90%] rounded-xl bg-gray-200 shadow-sm q-pa-md '
            'hover:shadow-md transition-all duration-200 z-0 box-border'
        ):
            with ui.row().classes('items-start justify-between w-full min-w-0'):
                ui.label(evt['title']).classes(
                    'text-body1 text-weight-medium truncate break-words max-w-[240px] md:max-w-[260px]'
                )
                ui.label(_date_badge(evt['date'])).classes('text-weight-bold text-grey-7')

            ui.separator().classes('q-my-sm')

            with ui.row().classes('items-center justify-between text-grey-8 text-caption w-full min-w-0'):
                ui.label(f"{evt.get('start','')} → {evt.get('end','')}").classes('truncate')
                if evt.get('recurring'):
                    with ui.row().classes('items-center gap-1 min-w-0'):
                        ui.icon('autorenew').classes('text-[16px]')
                        ui.label(evt['recurring']).classes('truncate')

            ui.separator().classes('q-my-sm')

            with ui.row().classes('items-center justify-around text-grey-7'):
                ui.icon('edit_note').classes('cursor-pointer hover:text-primary').on(
                    'click',
                    lambda _=None, ev=evt: open_edit_dialog(
                        ev,
                        on_save=lambda updated, original=ev: _update_event(original, updated),
                        on_delete=lambda original=ev: _remove_event(original),
                    )
                )
                ui.icon('delete').classes('cursor-pointer hover:text-negative').on(
                    'click', lambda _=None, original=evt: _remove_event(original)
                )

    # --------------------------------------------
    # FABs
    # --------------------------------------------
    with ui.button(
        icon="add",
        on_click=lambda: open_edit_dialog(None, on_save=_create_event),
    ) as new_event_button:
        new_event_button.props('fab color=primary')
        new_event_button.classes('fixed bottom-4 right-4 shadow-lg')

    with ui.button(icon="chat_bubble", on_click=lambda: ui.navigate.to('/assistant')) as assistant_button:
        assistant_button.props('fab color=primary')
        assistant_button.classes('fixed bottom-20 right-4 shadow-lg')

    # --------------------------------------------
    # Search bindings
    # --------------------------------------------
    debounce = {'t': None}

    def queue_refresh():
        if debounce['t']:
            debounce['t'].cancel()
        debounce['t'] = ui.timer(0.2, lambda: (refresh(), debounce.update(t=None)), once=True)

    search_box.on('input', lambda *_: queue_refresh())
    search_box.on('update:model-value', lambda *_: queue_refresh())
    search_box.on('clear', lambda *_: refresh())
    search_box.on('keydown.enter', lambda *_: refresh())
    search_box.on('keydown.backspace', lambda *_: queue_refresh())
    search_box.on('keydown.delete', lambda *_: queue_refresh())
    search_box.on('keydown.space', lambda *_: queue_refresh())
    search_box.on('paste', lambda *_: queue_refresh())
    search_box.on('cut', lambda *_: queue_refresh())
    search_box.on('compositionend', lambda *_: queue_refresh())
    search_box.on('blur', lambda *_: refresh())
    search_box.on('change', lambda *_: refresh())

    refresh()