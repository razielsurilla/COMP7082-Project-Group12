import unittest
from app.components.schedule_event import ScheduleEvent

class DummyInput:
    def __init__(self, value):
        self.value = value

class TestScheduleEvent(unittest.TestCase):

    def test_schedule_event_get_data(self):
        evt = ScheduleEvent({
            "event_name": "Lunch",
            "day_of_the_week": "Monday",
            "desc": "Cafeteria",
        })

        evt.input_name = DummyInput("Lunch")
        evt.input_day = DummyInput("Monday")
        evt.input_desc = DummyInput("Cafeteria")

        data = evt.get_data()

        self.assertEqual(data["event_name"], "Lunch")
        self.assertEqual(data["day_of_the_week"], "Monday")
        self.assertEqual(data["desc"], "Cafeteria")
