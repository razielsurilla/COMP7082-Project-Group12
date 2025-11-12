# app/components/reminder_component.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from nicegui import ui

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

def _minutes_from_labels(labels: List[str]) -> List[int]:
    mins: List[int] = []
    for label in labels:
        if label in REMINDER_OPTIONS:
            mins.append(REMINDER_OPTIONS[label])
    return sorted(set(mins))

class ReminderComponent:
    """Simplified reminder selector with preset checkboxes only."""
    def __init__(self, initial_minutes: Optional[List[int]] = None, initial_labels: Optional[List[str]] = None) -> None:
        if initial_minutes is not None:
            reverse = {v: k for k, v in REMINDER_OPTIONS.items()}
            labels = [reverse.get(m, f'{m} minutes before') for m in sorted(initial_minutes)]
        elif initial_labels is not None:
            labels = [l for l in initial_labels if isinstance(l, str)]
        else:
            labels = []
        self.selected_preset_labels: List[str] = [l for l in ALL_LABELS if l in labels]
        self._preset_checkboxes: Dict[str, ui.element] = {}

    def build(self, width_class: str = 'w-[92%] max-w-[460px]') -> None:
        ui.separator().classes(f'{width_class} q-my-sm')
        ui.label('Reminders').classes('text-body2 text-weight-medium self-start q-ml-md')

        with ui.element('div').classes(f'{width_class} grid grid-cols-1 md:grid-cols-2 gap-2'):
            for label in ALL_LABELS:
                cb = ui.checkbox(label, value=(label in self.selected_preset_labels))
                self._preset_checkboxes[label] = cb

    def get_labels_and_minutes(self) -> Tuple[List[str], List[int]]:
        selected_presets = [l for l, cb in self._preset_checkboxes.items() if cb.value]
        minutes = _minutes_from_labels(selected_presets)
        return selected_presets, minutes
