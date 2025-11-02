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
        self.month_select = None
        self.year_select = None

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
            with ui.grid(columns=7).classes('gap-x-4 gap-y-2 justify-center'):
                for weekday in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                    ui.label(weekday).classes('text-md font-bold text-center')
                    #TODO: Make Buttons
                for day in days:
                    is_current = day.month == self.state["month"]
                    is_today = day == self.today
                    bg = 'bg-white' if is_current else 'bg-gray-200'
                    if is_today:
                        bg = 'bg-blue-100'  # highlight today


                    def show_day_modal(day=day):
                        with ui.dialog() as dialog, ui.card().classes('p-4 w-80 h-120 flex items-center rounded-3xl relative bg-[#d9d9d9]'):
                            with ui.row().classes():
                                ui.icon('add').classes('text-black absolute top-4 right-4 text-2xl').on(
                                    'click', lambda: ui.navigate.to('/add-edit'))

                            ui.label(f"{calendar.month_name[day.month]} {day.day}, {day.year}").classes(
                                'text-xl font-bold text-center align-center'
                            )

                            # TODO: ForEach Event on Day, make event.
                            for i in range(1):
                                with ui.card().classes('w-60 h-20 p-2 flex justify-between'):
                                    #LS
                                    with ui.element('div').classes('block mr-auto'):
                                        ui.label("Event Name").classes('mb-5')
                                        if True: #If is a recurring event
                                            with ui.element('div').classes('flex'):
                                                ui.icon('cached').classes('pt-1 pr-1')
                                                ui.label("Every 2 Days")

                                    with ui.element('div').classes('block ml-auto justify-right items-end text-right'):
                                        ui.label(f"12:00")
                                        if True: #If event has end time
                                            ui.label("to")
                                            ui.label(f"1:00")



                        dialog.open()
                    # card is one day cell
                    #TODO: Make Clickable to pop up modal
                    with ui.card().classes(f'w-24 h-24 block p-2 {bg}').on('click', show_day_modal):
                        weekend = 'text-red' if (day.weekday() == 5 or day.weekday() == 6) else 'text-black'
                        ui.label(str(day.day)).classes(f'{weekend}')
                        if True: # TODO: Check if day has events, and check length
                            with ui.element('div').classes('flex'):
                                ui.icon('circle').classes('text-blue-500 text-xs pt-1 pr-1')
                                ui.label("One")
                        if True:
                            with ui.element('div').classes('flex'):
                                ui.icon('circle').classes('text-blue-500 text-xs pt-1 pr-1')
                                ui.label("Two")
                        if True: #if more than two events
                            num_events = 3 #TODO: Fix logic later
                            ui.label(f"+{num_events} More").classes('text-center')

    def prev_month(self):
        # wraparound jan -> dec
        if self.state["month"] == 1:
            self.state["month"] = 12
            self.state["year"] -= 1
        else:
            self.state["month"] -= 1
        # self.calendar_label.set_text(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}')
        self.render_calendar()  # redraw for prev month

    def next_month(self):
        # wraparound dec -> jan
        if self.state["month"] == 12:
            self.state["month"] = 1
            self.state["year"] += 1
        else:
            self.state["month"] += 1
        # self.calendar_label.set_text(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}')
        self.render_calendar()  # redraw for next month

    def update_state(self, month, year):
        self.state["month"] = month
        self.state["year"] = year

        if self.month_select:
            self.month_select.set_value(calendar.month_name[self.state["month"]])
        if self.year_select:
            self.year_select.set_value(str(self.state["year"]))

        self.render_calendar()

    def show(self):

        months = list(calendar.month_name)[1:]
        years = [str(y) for y in range(self.today.year - 1000, self.today.year + 1000)]

        # this is so everything is centered
        with ui.column().classes('justify-center items-center w-full'):    
            # month label on top
            #self.calendar_label = ui.label(f'{calendar.month_name[self.state["month"]]} {self.state["year"]}') \
            #                     .classes('text-3xl font-bold mb-4 justify-center text-center')
            # TODO: Make these dropdown menus with on_change events (set state, set text, render_calendar)
            with ui.row():
                def on_month_change(e):
                    month_index = months.index(e.value) + 1
                    self.update_state(month_index, self.state["year"])

                def on_year_change(e):
                    year_value = int(e.value)
                    self.update_state(self.state["month"], year_value)

                self.month_select = ui.select(
                    options=months,
                    value=calendar.month_name[self.state["month"]],
                    on_change=on_month_change
                )

                self.year_select = ui.select(
                    options=years,
                    value=str(self.state["year"]),
                    on_change=on_year_change
                )

                # Implement Later, not important for now
                # ui.button("Today", on_click=lambda: self.update_state(self.today.month, self.today.year))

            # row here, so the arrows are on the same row as the calendar
            with ui.row().classes('items-center justify-center gap-4'):
                ui.button('<', on_click=self.prev_month).classes('w-10 h-10 self-center')
                self.calendar_container = ui.column().classes('items-center')
                ui.button('>', on_click=self.next_month).classes('w-10 h-10 self-center')

            self.render_calendar()

class HomeTabs:
    def show(self):
        calendar_ui = Calendar()
        with ui.tabs().classes('w-full fixed bottom-0 left-0 h-10') as tabs:
            calendar_tab = ui.tab("Main Calendar")
            important_dates = ui.tab('Important Dates')
            upcoming_events = ui.tab('Upcoming Events')
        with ui.tab_panels(tabs, value=calendar_tab).classes('w-full p-0').props('animated=False'):
            with ui.tab_panel(calendar_tab).classes('p-0 overflow-hidden'):
                calendar_ui.show()
            with ui.tab_panel(important_dates).classes('pl-20'):
                ui.label("Important Dates")
            with ui.tab_panel(upcoming_events).classes('pl-20'):
                ui.label("Upcoming Events")
