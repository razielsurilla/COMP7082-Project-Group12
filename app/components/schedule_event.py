from nicegui import ui
class ScheduleEvent:
    def __init__(self, event):
        self.event = event

    def render(self):
        with ui.card().classes(
            "p-4 bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-all"
        ):
            ui.label(self.event.get("event", "Unknown Event")).classes(
                "text-lg font-bold text-gray-800 mb-1"
            )
            ui.label(self.event.get("date", "Unknown Date")).classes("text-sm text-gray-500")
            ui.label(self.event.get("description", "")).classes("text-sm text-gray-600 mt-1")
            ui.label(self.event.get("detail", "")).classes("text-sm text-gray-600 mt-1")

