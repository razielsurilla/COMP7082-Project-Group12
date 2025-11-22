# app/pages/upcoming_events.py
from __future__ import annotations
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import json

from nicegui import ui
from app.components.edit_event import open_edit_dialog
from app.sharedVars import AddEditEventData  # same DTO used in events.py


def _date_badge(iso_date: str) -> str:
    d = datetime.fromisoformat(iso_date).date()
    return f"{d.strftime('%b').upper()} {d.day}"


def _format_time_12h(dt: datetime) -> str:
    """Return times like '9:00 AM' / '1:05 PM' (no leading zero on hour)."""
    s = dt.strftime('%I:%M %p')  # e.g. '09:00 AM'
    if s.startswith('0'):
        s = s[1:]
    return s


def _event_date(evt: Dict[str, Any]) -> Optional[date]:
    # Prefer start_date, fall back to legacy 'date'
    d = evt.get('start_date') or evt.get('date')
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
    - Shows only this month's upcoming events (today and later in same month)
    """

    # ---- DB row -> UI dict ----
    def _from_data_frame(df: Any) -> Dict[str, Any]:
        start_dt = datetime.fromtimestamp(df.eventStartDate)
        end_dt = datetime.fromtimestamp(df.eventEndDate)

        start_date_str = start_dt.strftime('%Y-%m-%d')
        end_date_str = end_dt.strftime('%Y-%m-%d')
        start_str = _format_time_12h(start_dt)
        end_str = _format_time_12h(end_dt)

        # Frequency index -> label
        idx = int(getattr(df, 'recurringEventOptionIndex', 0) or 0)
        freq_labels = ['None', 'Daily', 'Weekly', 'Monthly']
        freq_label = freq_labels[idx] if 0 <= idx < len(freq_labels) else 'None'

        # Interval / recurringInterval (for "Every N days/weeks/months")
        recurring_interval = int(getattr(df, 'recurringInterval', 1) or 1)

        # Human-readable recurring text for UI + RecurringComponent
        rec_text: Optional[str] = None
        if freq_label != 'None':
            if recurring_interval <= 1:
                rec_text = freq_label  # 'Daily', 'Weekly', 'Monthly'
            else:
                unit_map = {'Daily': 'day', 'Weekly': 'week', 'Monthly': 'month'}
                unit = unit_map.get(freq_label, 'time')
                plural = 's' if recurring_interval != 1 else ''
                rec_text = f'Every {recurring_interval} {unit}{plural}'

        # End options from DB
        end_opt_idx = int(getattr(df, 'recurringEndOptionIndex', 0) or 0)

        raw_end_ts = getattr(df, 'recurringEndDate', None)
        if isinstance(raw_end_ts, (int, float)) and raw_end_ts > 0:
            end_date_iso = datetime.fromtimestamp(raw_end_ts).strftime('%Y-%m-%d')
        else:
            end_date_iso = None

        end_count = getattr(df, 'recurringEndCount', None)
        try:
            if end_count is not None:
                end_count = int(end_count)
        except Exception:
            end_count = None

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
            'start_date': start_date_str,
            'end_date': end_date_str,
            'start': start_str,
            'end': end_str,
            'recurring': rec_text,
            '_start_ts': df.eventStartDate,
            '_end_ts': df.eventEndDate,
            'description': getattr(df, 'eventDescription', '') or '',
            'is_recurring': bool(getattr(df, 'isRecurringEvent', False)),
            'is_alerting': bool(getattr(df, 'isAlerting', False)),
            'recurring_option_index': idx,
            'recurring_interval': recurring_interval,
            'recurring_end_option_index': end_opt_idx,
            'recurring_end_date': end_date_iso,
            'recurring_end_count': end_count,
            'selectedAlertCheckboxes': alert_labels,
            'reminders': alert_labels,
        }

    use_db = calendar_data is not None

    frames = calendar_data.getAllData() if use_db else []
    events: List[Dict[str, Any]] = [_from_data_frame(f) for f in frames]

    # ---- Header ----
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

        # default: show everything
        window_list: List[Dict[str, Any]] = base_list

        if use_db:
            now = datetime.now()
            today = now.date()
            now_ts = now.timestamp()
            window_list = []

            for e in base_list:
                evd = _event_date(e)
                if evd is None:
                    continue

                # Only show events in the current month that are not in the past.
                if evd.year == today.year and evd.month == today.month:

                    # Future day this month
                    if evd > today:
                        window_list.append(e)
                        continue

                    # Same day → only include if start timestamp is after now
                    if evd == today:
                        start_ts = e.get('_start_ts')
                        if isinstance(start_ts, (int, float)) and start_ts >= now_ts:
                            window_list.append(e)

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
                    start_date_str = (
                        updated.get('start_date', '') or updated.get('date', '')
                    )
                    end_date_str = updated.get('end_date', '') or start_date_str

                    start_str = updated.get('start', '')
                    end_str = updated.get('end', '')

                    new_start_ts = _parse_date_time(start_date_str, start_str)
                    new_end_ts = _parse_date_time(end_date_str, end_str)

                    # Build new AddEditEventData frame
                    frame = AddEditEventData()
                    frame.eventName = updated.get('title', '') or ''
                    frame.eventStartDate = new_start_ts
                    frame.eventEndDate = new_end_ts
                    frame.eventDescription = updated.get('description', '') or ''
                    frame.isRecurringEvent = bool(
                        updated.get('is_recurring') or updated.get('recurring')
                    )
                    frame.isAlerting = bool(updated.get('is_alerting', False))
                    frame.recurringEventOptionIndex = int(
                        updated.get('recurring_option_index', 0) or 0
                    )
                    frame.selectedAlertCheckboxes = (
                        updated.get('selectedAlertCheckboxes', []) or []
                    )

                    # interval + end options
                    frame.recurringInterval = int(
                        updated.get('recurring_interval', 1) or 1
                    )

                    frame.recurringEndOptionIndex = int(
                        updated.get('recurring_end_option_index', 0) or 0
                    )

                    end_date_iso = updated.get('recurring_end_date')
                    if end_date_iso:
                        try:
                            dt_end = datetime.strptime(
                                end_date_iso.strip(), '%Y-%m-%d'
                            )
                            frame.recurringEndDate = dt_end.timestamp()
                        except Exception:
                            frame.recurringEndDate = None
                    else:
                        frame.recurringEndDate = None

                    end_count_val = updated.get('recurring_end_count')
                    try:
                        frame.recurringEndCount = (
                            int(end_count_val)
                            if end_count_val is not None
                            else None
                        )
                    except Exception:
                        frame.recurringEndCount = None

                    calendar_data.updateEvent(
                        old_start_ts,  # original keys
                        old_end_ts,
                        frame,  # new data
                    )

                    # Update UI hidden keys
                    updated['_start_ts'] = new_start_ts
                    updated['_end_ts'] = new_end_ts
                    updated['id'] = f'{new_start_ts}-{new_end_ts}'

                except Exception as e:
                    print(f"[UPCOMING] updateEvent error: {e}")
                    ui.notify(
                        'Failed to update event in the database (upcoming_events).',
                        color='negative',
                    )
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
                    print(f"[UPCOMING] deleteEvent error: {e}")
                    ui.notify(
                        'Error deleting event from database (upcoming_events).',
                        color='negative',
                    )
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
            start_date_str = new_ev.get('start_date', '') or new_ev.get('date', '')
            end_date_str = new_ev.get('end_date', '') or start_date_str

            start_str = new_ev.get('start', '')
            end_str = new_ev.get('end', '')

            start_ts = _parse_date_time(start_date_str, start_str)
            end_ts = _parse_date_time(end_date_str, end_str)

            frame = AddEditEventData()
            frame.eventName = new_ev.get('title', '') or ''
            frame.eventStartDate = start_ts
            frame.eventEndDate = end_ts
            frame.eventDescription = new_ev.get('description', '') or ''
            frame.isRecurringEvent = bool(
                new_ev.get('is_recurring') or new_ev.get('recurring')
            )
            frame.isAlerting = bool(new_ev.get('is_alerting', False))
            frame.recurringEventOptionIndex = int(
                new_ev.get('recurring_option_index', 0) or 0
            )
            frame.selectedAlertCheckboxes = (
                new_ev.get('selectedAlertCheckboxes', []) or []
            )

            # interval + end options
            frame.recurringInterval = int(
                new_ev.get('recurring_interval', 1) or 1
            )

            frame.recurringEndOptionIndex = int(
                new_ev.get('recurring_end_option_index', 0) or 0
            )

            end_date_iso = new_ev.get('recurring_end_date')
            if end_date_iso:
                try:
                    dt_end = datetime.strptime(end_date_iso.strip(), '%Y-%m-%d')
                    frame.recurringEndDate = dt_end.timestamp()
                except Exception:
                    frame.recurringEndDate = None
            else:
                frame.recurringEndDate = None

            end_count_val = new_ev.get('recurring_end_count')
            try:
                frame.recurringEndCount = (
                    int(end_count_val) if end_count_val is not None else None
                )
            except Exception:
                frame.recurringEndCount = None

            try:
                calendar_data.addData(frame)
            except Exception as e:
                print(f"[UPCOMING] DB create error: {e}")
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
                    'text-body1 text-weight-medium truncate break-words '
                    'max-w-[240px] md:max-w-[260px]'
                )
                ui.label(_date_badge(evt['start_date'])).classes(
                    'text-weight-bold text-grey-7'
                )

            ui.separator().classes('q-my-sm')

            with ui.row().classes(
                'items-center justify-between text-grey-8 text-caption w-full min-w-0'
            ):
                ui.label(f"{evt.get('start','')} to {evt.get('end','')}").classes(
                    'truncate'
                )
                if evt.get('recurring'):
                    with ui.row().classes('items-center gap-1 min-w-0'):
                        ui.icon('autorenew').classes('text-[16px]')
                        ui.label(evt['recurring']).classes('truncate')

            ui.separator().classes('q-my-sm')

            with ui.row().classes('items-center justify-around text-grey-7'):
                ui.icon('edit_note').classes(
                    'cursor-pointer hover:text-primary'
                ).on(
                    'click',
                    lambda _=None, ev=evt: open_edit_dialog(
                        ev,
                        on_save=lambda updated, original=ev: _update_event(
                            original, updated
                        ),
                        on_delete=lambda original=ev: _remove_event(original),
                    ),
                )
                ui.icon('delete').classes(
                    'cursor-pointer hover:text-negative'
                ).on(
                    'click', lambda _=None, original=evt: _remove_event(original)
                )

    # ---- initial render ----
    refresh()
