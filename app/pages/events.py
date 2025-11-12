# app/pages/events.py
from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any, Optional
from nicegui import ui
from app.components.edit_event import open_edit_dialog

# --------------------------------------------------------------------
# DB HOOK 0: optionally accept a CalendarData instance from the route:
#     def show(calendar_data: Optional[CalendarData] = None) -> None:
# and pass it in from your route:
#     with_sidebar(lambda: events.show(CalendarData(sqlInstance)))
# --------------------------------------------------------------------


def _demo_events() -> List[Dict[str, Any]]:
    return [
        {'id': 1, 'title': 'Morning Standup',  'date': '2025-01-08', 'start': '9:00 AM',  'end': '9:30 AM',  'recurring': 'Daily'},
        {'id': 2, 'title': 'Design Review',    'date': '2025-01-09', 'start': '1:00 PM',  'end': '2:00 PM',  'recurring': None},
        {'id': 3, 'title': 'Lab Meeting',      'date': '2025-01-10', 'start': '10:00 AM', 'end': '11:30 AM', 'recurring': 'Weekly'},
        {'id': 4, 'title': 'Team Lunch',       'date': '2025-02-01', 'start': '12:00 PM', 'end': '1:00 PM',  'recurring': None},
    ]


def _date_badge(iso_date: str) -> str:
    d = datetime.fromisoformat(iso_date).date()
    return f"{d.strftime('%b').upper()} {d.day}"


# --------------------------------------------
# Main page
# --------------------------------------------
def show(calendar_data: Optional[Any] = None) -> None:
    """Events page with simple search and integrated Edit/Delete/New via dialog component."""

    # DB HOOK 1: INITIAL LOAD
    # Replace the line below with: events = calendar_data.list_all()
    events: List[Dict[str, Any]] = _demo_events() if calendar_data is None else calendar_data.list_all()

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
        # fallback identity or equality
        for i, e in enumerate(events):
            if e is original or e == original:
                return i
        return -1

    def refresh_from_db():
        """DB HOOK 2: RELOAD LIST from DB after create/update/delete."""
        nonlocal events
        if calendar_data is not None:
            events = calendar_data.list_all()

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
    # CRUD handlers (each has a DB HOOK)
    # --------------------------------------------
    def _update_event(original: Dict[str, Any], updated: Dict[str, Any]) -> None:
        """Edit -> Save"""
        # DB HOOK 3: UPDATE
        # If you have IDs, persist first:
        if calendar_data is not None:
            eid = updated.get('id') or original.get('id')
            if eid is not None:
                calendar_data.update(eid, updated)

        # Local list sync
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
        # DB HOOK 4: DELETE
        if calendar_data is not None and original.get('id') is not None:
            calendar_data.delete(original['id'])

        # Local list sync
        i = _find_index(original)
        if i >= 0:
            events.pop(i)

        if calendar_data is not None:
            refresh_from_db()
        refresh()

    def _create_event(new_ev: Dict[str, Any]) -> None:
        """New -> Save"""
        # DB HOOK 5: CREATE
        if calendar_data is not None:
            new_id = calendar_data.create(new_ev)  # should return the new ID
            new_ev['id'] = new_id

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
                        ui.icon('autorenew').classes('text-[16px]')  # size via class for NiceGUI
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
