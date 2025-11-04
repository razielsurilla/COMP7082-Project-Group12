# app/pages/events.py
from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any
from nicegui import ui
from app.components.edit_event import open_edit_dialog


def _demo_events() -> List[Dict[str, Any]]:
    return [
        {'title': 'Morning Standup',  'date': '2025-01-08', 'start': '9:00 AM',  'end': '9:30 AM',  'recurring': 'Daily'},
        {'title': 'Design Review',    'date': '2025-01-09', 'start': '1:00 PM',  'end': '2:00 PM',  'recurring': None},
        {'title': 'Lab Meeting',      'date': '2025-01-10', 'start': '10:00 AM', 'end': '11:30 AM', 'recurring': 'Weekly'},
        {'title': 'Team Lunch',       'date': '2025-02-01', 'start': '12:00 PM', 'end': '1:00 PM',  'recurring': None},
        {'title': 'Project Sync',     'date': '2025-02-03', 'start': '2:00 PM',  'end': '3:00 PM',  'recurring': None},
        {'title': 'Quarterly Review', 'date': '2025-03-05', 'start': '11:00 AM', 'end': '12:00 PM', 'recurring': 'Every 3 Months'},
    ]


def _date_badge(iso_date: str) -> str:
    d = datetime.fromisoformat(iso_date).date()
    return f"{d.strftime('%b').upper()} {d.day}"


def show() -> None:
    """Events page with simple search and integrated Edit/Delete/New via dialog component."""
    events: List[Dict[str, Any]] = _demo_events()

    # Prevent horizontal scroll globally
    ui.add_head_html('<style>html, body, #app { overflow-x: hidden !important; }</style>')

    # --- Header row (title centered, simple search on right) ---
    with ui.row().classes('items-center justify-between w-full max-w-[100vw] px-4 md:px-6 pt-4'):
        # left spacer to keep title centered
        ui.label().classes('w-[14rem] md:w-[20rem]')
        ui.label('Events').classes('text-h5 text-weight-bold text-black text-center flex-1')

        # simple search input
        search_box = ui.input(
            placeholder='Search title or date…',
        ).props('outlined dense clearable debounce=200').classes('w-[14rem] md:w-[20rem] max-w-full bg-gray-200')

    # --- Main container & grid ---
    container = ui.element('div').classes('w-full max-w-[100vw] px-4 md:px-6 pb-24')

    # ---------- helpers to mutate the list ----------
    def _find_index(original: Dict[str, Any]) -> int:
        # try identity
        for i, e in enumerate(events):
            if e is original:
                return i
        # fallback: value equality
        for i, e in enumerate(events):
            if e == original:
                return i
        return -1

    def _update_event(original: Dict[str, Any], updated: Dict[str, Any]) -> None:
        i = _find_index(original)
        if i >= 0:
            events[i] = updated
        else:
            events.append(updated)
        refresh()

    def _remove_event(original: Dict[str, Any]) -> None:
        i = _find_index(original)
        if i >= 0:
            events.pop(i)
            refresh()

    # ---------- one event card ----------
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
                ui.label(f"{evt['start']} → {evt['end']}").classes('truncate')
                if evt.get('recurring'):
                    with ui.row().classes('items-center gap-1 min-w-0'):
                        ui.icon('autorenew', size='16px')
                        ui.label(evt['recurring']).classes('truncate')

            ui.separator().classes('q-my-sm')

            with ui.row().classes('items-center justify-around text-grey-7'):
                # EDIT -> open dialog prefilled; Save will call _update_event; Delete will call _remove_event
                ui.icon('edit_note').classes('cursor-pointer hover:text-primary').on(
                    'click',
                    lambda _=None, ev=evt: open_edit_dialog(
                        ev,
                        on_save=lambda updated, original=ev: _update_event(original, updated),
                        on_delete=lambda original=ev: _remove_event(original),
                    )
                )
                # DELETE (immediate)
                ui.icon('delete').classes('cursor-pointer hover:text-negative').on(
                    'click', lambda _=None, original=evt: _remove_event(original)
                )

    # ---------- render grid ----------
    def refresh():
        container.clear()
        q = (search_box.value or '').strip().lower()

        if q:
            filtered: List[Dict[str, Any]] = []
            for e in events:
                hay = ' '.join([
                    e['title'],
                    e['date'],
                    e.get('start', ''),
                    e.get('end', ''),
                    str(e.get('recurring', '')),
                ]).lower()
                if q in hay:
                    filtered.append(e)
        else:
            filtered = events

        with container:
            with ui.element('div').classes(
                # two columns on md+, one on small; slight right shift with pl-6 per your version
                'grid grid-cols-1 md:grid-cols-2 gap-6 justify-items-center w-full pl-10'
            ):
                for evt in filtered:
                    _event_card(evt)

    # --- FABs (New & Assistant) ---
    with ui.button(
        icon="add",
        on_click=lambda: open_edit_dialog(
            None,
            on_save=lambda new_ev: (events.append(new_ev), refresh()),
        ),
    ) as new_event_button:
        new_event_button.props('fab color=primary')
        new_event_button.classes('fixed bottom-4 right-4 shadow-lg')

    with ui.button(icon="chat_bubble", on_click=lambda: ui.navigate.to('/assistant')) as assistant_button:
        assistant_button.props('fab color=primary')
        assistant_button.classes('fixed bottom-20 right-4 shadow-lg')

    # --- search bindings ---
    search_box.on('input', refresh)
    search_box.on('clear', refresh)
    search_box.on('keydown.enter', refresh)
    search_box.on('keydown.backspace', refresh)

    refresh()
