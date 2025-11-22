# app/components/recurring_event.py
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
from nicegui import ui
import re

# ----- Constants -----
FREQ_LABELS = ['None', 'Daily', 'Weekly', 'Monthly']
FREQ_TO_RRULE = {'Daily': 'DAILY', 'Weekly': 'WEEKLY', 'Monthly': 'MONTHLY'}
END_KIND_LABELS = ['Never', 'On date', 'After occurrences']


# ----- Helpers -----
def _is_date(v: str) -> bool:
    try:
        datetime.strptime((v or '').strip(), '%Y-%m-%d')
        return True
    except Exception:
        return False


def _to_iso_date_str(v: Any) -> Optional[str]:
    if not v:
        return None
    if isinstance(v, str):
        return v if _is_date(v) else None
    try:
        return v.strftime('%Y-%m-%d')
    except Exception:
        return None


def _parse_recurring_text(text: Optional[str]) -> Tuple[str, int]:
    """Parse 'Every X days/weeks/months' into (freq_label, interval)."""
    if not text:
        return 'None', 1
    t = text.strip().lower()
    if t in ('daily', 'weekly', 'monthly'):
        return t.capitalize(), 1

    m = re.search(r'\bevery\s+(\d+)\s+(day|days)\b', t)
    if m:
        return 'Daily', max(1, int(m.group(1)))

    m = re.search(r'\bevery\s+(\d+)\s+(week|weeks)\b', t)
    if m:
        return 'Weekly', max(1, int(m.group(1)))

    m = re.search(r'\bevery\s+(\d+)\s+(month|months)\b', t)
    if m:
        return 'Monthly', max(1, int(m.group(1)))

    return 'None', 1


def _recurring_human(
    freq_label: str,
    interval: int,
    until: Optional[str] = None,
    count: Optional[int] = None,
) -> Optional[str]:
    """Convert recurrence structure to human-readable text."""
    if freq_label == 'None':
        return None
    unit = {'Daily': 'Days', 'Weekly': 'Weeks', 'Monthly': 'Months'}[freq_label]
    base = f'Every {interval} {unit}' if interval > 1 else freq_label
    if until:
        return f'{base} until {until}'
    if count:
        return f'{base} for {count} {"time" if count == 1 else "times"}'
    return base


# ----- Component -----
class RecurringComponent:
    def __init__(self, original: Optional[Dict[str, Any]] = None) -> None:
        original = original or {}

        # 1) Frequency + interval from human text (e.g. "Daily", "Every 2 weeks")
        self.freq_label, self.interval = _parse_recurring_text(original.get('recurring'))

        # 2) Structured recurrence definition (old style)
        self.rec_struct = original.get('recurrence') or {}

        # End-condition fields (UI state)
        self.end_kind = 'Never'
        self.end_date: Optional[str] = None
        self.end_count: Optional[int] = None

        used_struct = False

        # Prefer existing recurrence struct if it exists
        if isinstance(self.rec_struct, dict) and self.rec_struct:
            u = _to_iso_date_str(self.rec_struct.get('until'))
            if u:
                self.end_kind, self.end_date = 'On date', u
                used_struct = True
            else:
                try:
                    c = int(self.rec_struct.get('count') or 0)
                    if c > 0:
                        self.end_kind, self.end_count = 'After occurrences', c
                        used_struct = True
                except Exception:
                    pass

        # 3) If no struct or no end info, fall back to DB-style fields
        if not used_struct:
            end_opt = int(original.get('recurring_end_option_index') or 0)
            if end_opt == 1:
                self.end_kind = 'On date'
                self.end_date = _to_iso_date_str(original.get('recurring_end_date'))
            elif end_opt == 2:
                self.end_kind = 'After occurrences'
                try:
                    c = int(original.get('recurring_end_count') or 0)
                    if c > 0:
                        self.end_count = c
                except Exception:
                    pass
            else:
                self.end_kind = 'Never'

        # UI elements (placeholders, set in build())
        self.recurring_sel: Optional[ui.select] = None
        self.interval_inp: Optional[ui.number] = None
        self.ends_row: Optional[ui.row] = None
        self.ends_sel: Optional[ui.select] = None
        self.ends_date_inp: Optional[ui.input] = None
        self.ends_count_inp: Optional[ui.number] = None

    # ----- Build UI -----
    def build(self, width_class: str = 'w-[92%] max-w-[460px]') -> None:
        ui.label('Recurring').classes('text-body2 text-weight-medium self-start q-ml-md')

        # Row 1: Frequency + Interval
        with ui.row().classes(f'{width_class} items-center gap-3'):
            self.recurring_sel = ui.select(
                options=FREQ_LABELS,
                value=self.freq_label,
                label='Frequency',
            ).props('outlined dense').classes('min-w-[160px]')

            self.interval_inp = ui.number(
                label='Every … (interval)',
                value=self.interval,
                min=1,
                max=365,
            ).props('outlined dense').classes('w-[160px]')

        # Row 2: Ends + On date + Occurrences (all aligned)
        with ui.row().classes(f'{width_class} items-center gap-3') as self.ends_row:
            self.ends_sel = ui.select(
                options=END_KIND_LABELS,
                value=self.end_kind,
                label='Ends',
            ).props('outlined dense').classes('min-w-[160px]')

            # End date input (same row)
            self.ends_date_inp = ui.input(
                label='End date (YYYY-MM-DD)',
                value=self.end_date or '',
                validation={
                    'Enter a valid date as YYYY-MM-DD': (
                        lambda v: True if not (v or '').strip() else _is_date(v)
                    )
                },
            ).props('outlined dense clearable').classes('w-[160px] !pb-0')

            # Occurrence count (same row)
            self.ends_count_inp = ui.number(
                label='Occurrences',
                value=self.end_count if self.end_count is not None else None,
                min=1,
                max=10000,
            ).props('outlined dense').classes('w-[160px]')

        # Reactive visibility bindings
        self.interval_inp.bind_enabled_from(
            self.recurring_sel,
            'value',
            backward=lambda v: v != 'None',
        )
        self.ends_row.bind_visibility_from(
            self.recurring_sel,
            'value',
            backward=lambda v: v != 'None',
        )
        self.ends_date_inp.bind_visibility_from(
            self.ends_sel,
            'value',
            backward=lambda v: v == 'On date',
        )
        self.ends_count_inp.bind_visibility_from(
            self.ends_sel,
            'value',
            backward=lambda v: v == 'After occurrences',
        )

    # ----- Getters -----
    def get_values(self) -> Tuple[str, int, Optional[str], Optional[int]]:
        """
        Returns:
            freq_label: 'None' | 'Daily' | 'Weekly' | 'Monthly'
            interval: int >= 1
            until_iso: 'YYYY-MM-DD' or None
            count_val: int or None
        """
        freq = (self.recurring_sel.value if self.recurring_sel else self.freq_label) or 'None'
        interval = int(self.interval_inp.value or 0) if self.interval_inp else self.interval
        kind = (self.ends_sel.value if self.ends_sel else self.end_kind) or 'Never'
        until_iso: Optional[str] = None
        count_val: Optional[int] = None

        if freq != 'None':
            if (
                kind == 'On date'
                and self.ends_date_inp
                and _is_date(self.ends_date_inp.value or '')
            ):
                until_iso = (self.ends_date_inp.value or '').strip()
            elif kind == 'After occurrences' and self.ends_count_inp:
                try:
                    c = int(self.ends_count_inp.value or 0)
                    if c > 0:
                        count_val = c
                except Exception:
                    pass

        return freq, interval, until_iso, count_val

    def get_human_and_struct(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Returns:
            human: e.g. 'Daily', 'Every 2 Weeks until 2025-02-10', or None
            struct: e.g. {'freq': 'WEEKLY', 'interval': 2, 'until': '2025-02-10'}
                    or None if no recurrence
        """
        freq, interval, until_iso, count_val = self.get_values()
        if freq == 'None' or interval < 1:
            return None, None

        human = _recurring_human(freq, interval, until=until_iso, count=count_val)

        struct: Dict[str, Any] = {
            'freq': FREQ_TO_RRULE[freq],
            'interval': interval,
        }
        if until_iso:
            struct['until'] = until_iso
        if count_val:
            struct['count'] = count_val

        return human, struct