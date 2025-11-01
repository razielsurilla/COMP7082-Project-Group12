from nicegui import ui
from datetime import date, timedelta
import calendar

# TODO: this should be a component, then home.py should create a Calendar object
class Calendar:
    def __init__(self):
        self.today = date.today()
        self.state = {"year": self.today.year, "month": self.today.month}
        self.calendar_container = None
        self.calendar_label = None

    def generate_month(self, year: int, month: int):
        first_day = date(year, month, 1)

        # find the sunday before the first day so grid is always 7x6
        start_day = first_day - timedelta(days=(first_day.weekday() + 1) % 7)

        # 6 weeks displayed, so 42 days
        return [start_day + timedelta(days=i) for i in range(42)]

    def render_calendar(self):
        self.calendar_container.clear()  # clear old calendar or it stacks
        days = self.generate_month(self.state["year"], self.state["month"])

        with self.calendar_container:
            with ui.grid(columns=7).classes('gap-2 justify-center'):
                for weekday in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                    ui.label(weekday).classes('text-md font-bold text-center')
                    #TODO: Make Sat/Sun Red
                    #TODO: Make Buttons
                for day in days:
                    is_current = day.month == self.state["month"]
                    is_today = day == self.today
                    bg = 'bg-white' if is_current else 'bg-gray-100'
                    if is_today:
                        bg = 'bg-blue-200'  # highlight today

                    # card is one day cell
                    with ui.card().classes(f'w-20 h-20 flex items-center justify-center {bg}'):
                        ui.label(str(day.day))

    def prev_month(self):
        # wraparound jan -> dec
        if self.state["month"] == 1:
            self.state["month"] = 12
            self.state["year"] -= 1
        else:
            self.state["month"] -= 1
        self.calendar_label.set_text(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}')
        self.render_calendar()  # redraw for prev month

    def next_month(self):
        # wraparound dec -> jan
        if self.state["month"] == 12:
            self.state["month"] = 1
            self.state["year"] += 1
        else:
            self.state["month"] += 1
        self.calendar_label.set_text(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}')
        self.render_calendar()  # redraw for next month

    def show(self):
        # this is so everything is centered
        with ui.column().classes('justify-center items-center w-full'):    
            # month label on top
            self.calendar_label = ui.label(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}') \
                                 .classes('text-3xl font-bold mb-4 justify-center text-center')
            # TODO: Make these dropdown menus with on_change events (set state, set text, render_calendar)

            # row here, so the arrows are on the same row as the calendar
            with ui.row().classes('items-center justify-center gap-4'):
                ui.button('<', on_click=self.prev_month).classes('w-10 h-10 self-center')
                self.calendar_container = ui.column().classes('items-center')
                ui.button('>', on_click=self.next_month).classes('w-10 h-10 self-center')

            self.render_calendar()

class HomeTabs:
    def show(self):
        calendar_ui = Calendar()
        with ui.tabs().classes('w-full fixed bottom-0 left-0') as tabs:
            calendar_tab = ui.tab("Main Calendar")
            important_dates = ui.tab('Important Dates')
            upcoming_events = ui.tab('Upcoming Events')
        with ui.tab_panels(tabs, value=calendar_tab).classes('w-full').props('animated=False'):
            with ui.tab_panel(calendar_tab):
                calendar_ui.show()
            with ui.tab_panel(important_dates).classes('pl-20'):
                ui.label("Important Dates")
            with ui.tab_panel(upcoming_events).classes('pl-20'):
                ui.label("Upcoming Events")
