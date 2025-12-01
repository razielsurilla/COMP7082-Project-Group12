from app.components.recurring_event import (
    RecurringComponent,
    _parse_recurring_text,
    _recurring_human,
)

def test_parse_recurring_text_simple():
    assert _parse_recurring_text("Daily") == ("Daily", 1)
    assert _parse_recurring_text("Every 3 days") == ("Daily", 3)
    assert _parse_recurring_text("Every 2 weeks") == ("Weekly", 2)

def test_parse_recurring_text_invalid():
    assert _parse_recurring_text(None) == ("None", 1)
    assert _parse_recurring_text("") == ("None", 1)

def test_recurring_human():
    assert _recurring_human("Daily", 1) == "Daily"
    assert _recurring_human("Weekly", 2) == "Every 2 Weeks"
    assert _recurring_human("Monthly", 1, until="2025-01-01") == "Monthly until 2025-01-01"
    assert _recurring_human("Yearly", 1, count=3) == "Yearly for 3 times"

def test_recurring_component_initialization_basic():
    comp = RecurringComponent({"recurring": "Every 2 weeks"})
    assert comp.freq_label == "Weekly"
    assert comp.interval == 2
    assert comp.end_kind == "Never"
