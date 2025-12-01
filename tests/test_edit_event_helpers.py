import unittest
from app.components.edit_event import (
    _parse_time_to_minutes,
    _minutes_to_12h_str,
    _to_time_input_value,
    _is_date,
)

class TestEditEventHelpers(unittest.TestCase):

    def test_parse_time_to_minutes_valid(self):
        self.assertEqual(_parse_time_to_minutes("9:00 AM"), 9*60)
        self.assertEqual(_parse_time_to_minutes("21:30"), 21*60 + 30)

    def test_parse_time_to_minutes_invalid(self):
        self.assertIsNone(_parse_time_to_minutes(""))
        self.assertIsNone(_parse_time_to_minutes("notatime"))

    def test_minutes_to_12h_str(self):
        self.assertEqual(_minutes_to_12h_str(9*60), "9:00 AM")
        self.assertEqual(_minutes_to_12h_str(13*60), "1:00 PM")
        self.assertEqual(_minutes_to_12h_str(None), "")

    def test_to_time_input_value(self):
        self.assertEqual(_to_time_input_value("9:00 AM"), "09:00")
        self.assertEqual(_to_time_input_value("21:30"), "21:30")
        self.assertEqual(_to_time_input_value("nope"), "")

    def test_is_date(self):
        self.assertTrue(_is_date("2024-01-20"))
        self.assertFalse(_is_date("20-01-2024"))
        self.assertFalse(_is_date(""))
