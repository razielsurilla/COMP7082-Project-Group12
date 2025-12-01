import pytest
from app.components.schedule_event import ScheduleEvent

class DummyInput:
    """Simple mock for NiceGUI input widget."""
    def __init__(self, value):
        self.value = value

def test_schedule_event_get_data():
    evt = ScheduleEvent({"event_name": "Lunch", "day_of_the_week": "Monday", "desc": "Cafeteria"})

    evt.input_name = DummyInput("Lunch")
    evt.input_day = DummyInput("Monday")
    evt.input_desc = DummyInput("Cafeteria")

    data = evt.get_data()
    assert data["event_name"] == "Lunch"
    assert data["day_of_the_week"] == "Monday"
    assert data["desc"] == "Cafeteria"
