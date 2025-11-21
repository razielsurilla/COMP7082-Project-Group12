# app/pages/upcoming_events.py
from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json

from nicegui import ui
from app.components.edit_event import open_edit_dialog
from app.sharedVars import AddEditEventData  # same DTO used in events.py


def _demo_events() -> List[Dict[str, Any]]:
    return [
        {'id': 1, 'title': 'Morning Standup', 'date': '2025-01-08', 'start': '9:00 AM',  'end': '9:30 AM',  'recurring': 'Daily'},
        {'id': 2, 'title': 'Design Review',   'date': '2025-01-09', 'start': '1:00 PM',  'end': '2:00 PM',  'recurring': None},
        {'id': 3, 'title': 'Lab Meeting',     'date': '2025-01-10', 'start': '10:00 AM', 'end': '11:30 AM', 'recurring': 'Weekly'},
        {'id': 4, 'title': 'Team Lunch',      'date': '2025-02-01', 'start': '12:00 PM', 'end': '1:00 PM',  'recurring': None},
    ]


def _date_badge(iso_date: str) -> str:
    d = datetime.fromisoformat(iso_date).date()
    return f"{d.strftime('%b').upper()} {d.day}"


def _event_date(evt: Dict[str, Any]) -> Optional[date]:
    d = evt.get('date')
    if not d:
        return None
    try:
        return datetime.fromisoformat(str(d)).date()
    except Exception:
        return None


def _parse_date_time(date_str: str, time_str: str) -> float:
    date_str = (date_str or '').strip()
    time_str = (time_str or '').strip()
    if not date_str or not time_str:
        raise ValueError("Missing date or time for event")

    joined = f'{date_str} {time_str}'
    for fmt in ('%Y-%m-%d %I:%M %p', '%Y-%m-%d %H:%M'):
        try:
            dt = datetime.strptime(joined, fmt)
            return dt.timestamp()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date/time: '{joined}'")


def build_upcoming_events(calendar_data: Optional[Any] = None) -> None:
    """
    Component-only builder used inside the Home 'Upcoming Events' tab.
    - Uses DB if calendar_data is provided
    - Seeds demo events if DB is empty
    - Shows only next 2 weeks of events (today .. today + 14 days)
    """

    # ---- DB row -> UI dict ----
    def _from_data_frame(df: Any) -> Dict[str, Any]:
        start_dt = datetime.fromtimestamp(df.eventStartDate)
        end_dt = datetime.fromtimestamp(df.eventEndDate)

        date_str = start_dt.strftime('%Y-%m-%d')
        start_str = start_dt.strftime('%I:%M %p').lstrip('0')
        end_str = end_dt.strftime('%I:%M %p').lstrip('0')

        idx = int(getattr(df, 'recurringEventOptionIndex', 0) or 0)
        freq_labels = ['None', 'Daily', 'Weekly', 'Monthly']
        freq_label = freq_labels[idx] if 0 <= idx < len(freq_labels) else 'None'
        recurring_label = None if freq_label == 'None' else freq_label

        raw_alert = getattr(df, 'selectedAlertCheckboxes', []) or []
        if isinstance(raw_alert, str):
            try:
                alert_labels = json.loads(raw_alert)
            except Exception:
                alert_labels = []
        else:
            alert_labels = list(raw_alert)

        return {
            'id': f'{df.eventStartDate}-{df.eventEndDate}',
            'title': df.eventName,
            'date': date_str,
            'start': start_str,
            'end': end_str,
            'recurring': recurring_label,
            '_start_ts': df.eventStartDate,
            '_end_ts': df.eventEndDate,
            'description': getattr(df, 'eventDescription', '') or '',
            'is_recurring': bool(getattr(df, 'isRecurringEvent', False)),
            'is_alerting': bool(getattr(df, 'isAlerting', False)),
            'recurring_option_index': idx,
            'selectedAlertCheckboxes': alert_labels,
            'reminders': alert_labels,
        }

    # ---- Seed demo events if DB empty ----
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
            frame.isRecurringEvent = bool(d.get('recurring'))
            frame.isAlerting = False
            frame.recurringEventOptionIndex = 0
            frame.selectedAlertCheckboxes = []
            calendar_data.addData(frame)

    use_db = calendar_data is not None

    if use_db:
        _seed_demo_events_if_empty()
        frames = calendar_data.getAllData()
        events: List[Dict[str, Any]] = [_from_data_frame(f) for f in frames]
    else:
        events = _demo_events()

    # ---- Header (component style, no back button, no bottom bar) ----
    with ui.row().classes('items-center justify-between w-full px-4 pt-4'):
        ui.label('Upcoming Events').classes('text-h6 text-weight-bold text-black')
        month_label = ui.label('').classes('text-body2 text-grey-7')

    container = ui.element('div').classes('w-full max-w-[100vw] px-4 md:px-6 pb-24')

    # ---- helpers ----
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
        nonlocal events
        if use_db:
            frames2 = calendar_data.getAllData()
            events = [_from_data_frame(f) for f in frames2]

    def _update_month_label(current_events: List[Dict[str, Any]]) -> None:
        if not current_events:
            d = date.today()
        else:
            dates = [d for d in (_event_date(e) for e in current_events) if d is not None]
            d = min(dates) if dates else date.today()
        month_label.text = f"{d.strftime('%b').upper()} {d.year}"

    def refresh():
        container.clear()
        base_list: List[Dict[str, Any]] = events

        if use_db:
            now = datetime.now()
            today = now.date()
            now_ts = now.timestamp()
            window_list: List[Dict[str, Any]] = []

            for e in base_list:
                evd = _event_date(e)
                if evd is None:
                    continue

                # ---------- NEW FIX ----------
                # Only show events IN THE SAME MONTH that are still upcoming.
                if evd.year == today.year and evd.month == today.month:

                    # Case 1: future day this month → always include
                    if evd > today:
                        window_list.append(e)
                        continue

                    # Case 2: same day → only include if start timestamp is after now
                    if evd == today:
                        start_ts = e.get('_start_ts')
                        if isinstance(start_ts, (int, float)) and start_ts >= now_ts:
                            window_list.append(e)
                # ---------- END FIX ----------

        else:
            # Demo mode → show all
            window_list = base_list

        # --- Sorting and draw ---
        def sort_key(e: Dict[str, Any]):
            evd = _event_date(e) or date.max
            return (evd.isoformat(), str(e.get('start', '')))

        window_list.sort(key=sort_key)
        _update_month_label(window_list)

        with container:
            with ui.element('div').classes(
                    'grid grid-cols-1 md:grid-cols-2 gap-6 justify-items-center w-full pl-0 md:pl-0'
            ):
                for evt in window_list:
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

    # ---- One event card ----
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
                ui.label(f"{evt.get('start','')} to {evt.get('end','')}").classes('truncate')
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

    # ---- initial render ----
    refresh()
