import pytest
from app.components.edit_event import (
    _parse_time_to_minutes,
    _minutes_to_12h_str,
    _to_time_input_value,
    _is_date,
)

def test_parse_time_to_minutes_valid():
    assert _parse_time_to_minutes("9:00 AM") == 9*60
    assert _parse_time_to_minutes("21:30") == 21*60 + 30

def test_parse_time_to_minutes_invalid():
    assert _parse_time_to_minutes("") is None
    assert _parse_time_to_minutes("notatime") is None

def test_minutes_to_12h_str():
    assert _minutes_to_12h_str(9*60) == "9:00 AM"
    assert _minutes_to_12h_str(13*60) == "1:00 PM"
    assert _minutes_to_12h_str(None) == ""

def test_to_time_input_value():
    assert _to_time_input_value("9:00 AM") == "09:00"
    assert _to_time_input_value("21:30") == "21:30"
    assert _to_time_input_value("nope") == ""

def test_is_date():
    assert _is_date("2024-01-20") is True
    assert _is_date("20-01-2024") is False
    assert _is_date("") is False
