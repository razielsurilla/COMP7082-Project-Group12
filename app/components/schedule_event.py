from nicegui import ui
from datetime import datetime, timedelta

class ScheduleEvent:
    def __init__(self, event):
        self.event = event
        self.input_name = None
        self.input_day = None
        self.input_desc = None

        # these fields are not relevant to the event and are not editable
        self.start_date = None
        self.end_date = None
        self.recurring = True    # always true
        self.alerting = True     # always true

    def get_data(self):
        return {
            "event_name": self.input_name.value,
            "day_of_the_week": self.input_day.value,
            "desc": self.input_desc.value
        }

    def render(self):
        with ui.card().classes(
            "p-4 bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-all"
        ):
            self.input_name = ui.input(
                label="Event",
                value=self.event.get("event_name", "Unknown Event")
            ).classes("text-sm text-gray-600 mb-1")

            self.input_day = ui.select(
                label="",
                options=[
                    "Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"
                ],
                value=self.event.get("day_of_the_week", "")
            ).classes("text-sm text-gray-600 mt-1")

            self.input_desc = ui.input(
                label="",
                value=self.event.get("desc", "")
            ).classes("text-sm text-gray-600 mt-1")

class UploadedEventDataFrame:
    def __init__(self, name, day, desc):
        self.eventName = name
        self.eventDescription = desc
        
        weekday_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        today = datetime.today()
        target = weekday_map.get(day, today.weekday())
        days_ahead = (target - today.weekday()) % 7
        event_date = today + timedelta(days=days_ahead)

        self.eventStartDate = event_date.timestamp()
        self.eventEndDate = (event_date + timedelta(hours=1)).timestamp()

        self.isRecurringEvent = True
        self.isAlerting = True

        self.recurringEventOptionIndex = 0
        self.selectedAlertCheckboxes = []        
