import unittest
from app.components.recurring_event import (
    RecurringComponent,
    _parse_recurring_text,
    _recurring_human,
)

class TestRecurringEvent(unittest.TestCase):

    def test_parse_recurring_text_simple(self):
        self.assertEqual(_parse_recurring_text("Daily"), ("Daily", 1))
        self.assertEqual(_parse_recurring_text("Every 3 days"), ("Daily", 3))
        self.assertEqual(_parse_recurring_text("Every 2 weeks"), ("Weekly", 2))

    def test_parse_recurring_text_invalid(self):
        self.assertEqual(_parse_recurring_text(None), ("None", 1))
        self.assertEqual(_parse_recurring_text(""), ("None", 1))

    def test_recurring_human(self):
        self.assertEqual(_recurring_human("Daily", 1), "Daily")
        self.assertEqual(_recurring_human("Weekly", 2), "Every 2 Weeks")
        self.assertEqual(
            _recurring_human("Monthly", 1, until="2025-01-01"),
            "Monthly until 2025-01-01",
        )
        self.assertEqual(
            _recurring_human("Yearly", 1, count=3),
            "Yearly for 3 times",
        )

    def test_recurring_component_initialization_basic(self):
        comp = RecurringComponent({"recurring": "Every 2 weeks"})
        self.assertEqual(comp.freq_label, "Weekly")
        self.assertEqual(comp.interval, 2)
        self.assertEqual(comp.end_kind, "Never")
